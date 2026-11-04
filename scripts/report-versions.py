#!/usr/bin/env python3
"""Inventory platform and lab dependency versions.

This is a Wave 0 tool for the latest-supported-GA upgrade programme. It reads
the repository rather than a hand-maintained list, so the baseline cannot drift
silently.

Examples:
    python scripts/report-versions.py
    python scripts/report-versions.py --platform-only
    python scripts/report-versions.py --json -o versions-report.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_SCOPES = (
    "platform/labs/",
    "platform/templates/",
    "platform/UbuntuBox/",
    "platform/rangebox/",
    "platform/tester/",
    "RangeBox/",
    "UbuntuBox/",
    "RemnuxBox/",
)
REQUIREMENT_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(?P<spec>==|>=|<=|~=|!=|>|<).*$"
)
FROM_RE = re.compile(r"^\s*FROM\s+(?P<image>[^\s#]+)", re.IGNORECASE)
USES_RE = re.compile(r"^\s*uses:\s*(?P<action>[^\s#]+)")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def in_lab_scope(path: Path) -> bool:
    return any(rel(path).startswith(prefix) for prefix in LAB_SCOPES)


def parse_requirements(path: Path) -> dict[str, str]:
    versions: dict[str, str] = {}
    if not path.is_file():
        return versions
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = REQUIREMENT_RE.match(line)
        if match:
            versions[match.group("name").lower()] = f"{match.group('spec')}{line.split(match.group('spec'), 1)[1].split()[0]}"
    return versions


def parse_package_json(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {"dependencies": {}, "devDependencies": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "dependencies": data.get("dependencies") or {},
        "devDependencies": data.get("devDependencies") or {},
    }


def parse_lockfile(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    locked: dict[str, str] = {}
    for name, entry in (data.get("packages") or {}).items():
        if not name.startswith("node_modules/"):
            continue
        package = name.split("node_modules/", 1)[1]
        if "version" in entry:
            locked[package] = entry["version"]
    return locked


def parse_dockerfiles(platform_only: bool) -> dict[str, list[str]]:
    images: dict[str, list[str]] = defaultdict(list)
    for path in ROOT.rglob("Dockerfile"):
        if platform_only and in_lab_scope(path):
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = FROM_RE.match(line)
            if match:
                image = match.group("image")
                path_label = rel(path)
                if image.lower() != "scratch" and path_label not in images[image]:
                    images[image].append(path_label)
    return dict(sorted(images.items(), key=lambda item: (-len(item[1]), item[0])))


def parse_compose(platform_only: bool) -> dict[str, list[str]]:
    images: dict[str, list[str]] = defaultdict(list)
    for path in list(ROOT.rglob("docker-compose*.yml")) + list(ROOT.rglob("docker-compose*.yaml")):
        if platform_only and in_lab_scope(path):
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("image:"):
                images[stripped.split(":", 1)[1].strip()].append(rel(path))
    return dict(sorted(images.items(), key=lambda item: item[0]))


def parse_workflows() -> dict[str, list[str]]:
    actions: dict[str, list[str]] = defaultdict(list)
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = USES_RE.match(line)
            if match:
                path_label = rel(path)
                if path_label not in actions[match.group("action")]:
                    actions[match.group("action")].append(path_label)
    return dict(sorted(actions.items(), key=lambda item: item[0]))


def collect(platform_only: bool) -> dict:
    backend_dir = ROOT / "platform" / "backend"
    frontend_dir = ROOT / "platform" / "frontend"
    package = parse_package_json(frontend_dir / "package.json")
    return {
        "generated_from": rel(ROOT),
        "platform_only": platform_only,
        "backend_requirements": parse_requirements(backend_dir / "requirements.txt"),
        "backend_dev_requirements": parse_requirements(backend_dir / "requirements-dev.txt"),
        "frontend_declared": package,
        "frontend_locked": parse_lockfile(frontend_dir / "package-lock.json"),
        "docker_bases": parse_dockerfiles(platform_only),
        "compose_images": parse_compose(platform_only),
        "github_actions": parse_workflows(),
    }


def markdown(report: dict) -> str:
    lines = [
        "# Version inventory",
        "",
        f"Generated from `{report['generated_from']}`"
        + (" (platform scope; lab/RangeBox images excluded)." if report["platform_only"] else "."),
        "",
        "## Backend requirements",
        "",
        "| Package | Version/spec |",
        "|---|---|",
    ]
    for name, version in sorted(report["backend_requirements"].items()):
        lines.append(f"| `{name}` | `{version}` |")
    lines += ["", "### Development/test", "", "| Package | Version/spec |", "|---|---|"]
    for name, version in sorted(report["backend_dev_requirements"].items()):
        lines.append(f"| `{name}` | `{version}` |")

    lines += ["", "## Frontend", "", "| Package | Declared | Locked |", "|---|---|---|"]
    declared = {}
    declared.update(report["frontend_declared"].get("dependencies") or {})
    declared.update(report["frontend_declared"].get("devDependencies") or {})
    for name in sorted(declared):
        lines.append(f"| `{name}` | `{declared[name]}` | `{report['frontend_locked'].get(name, '-')}` |")

    lines += ["", "## Container base images", "", "| Image | Uses | Files |", "|---|---|---|"]
    for image, paths in report["docker_bases"].items():
        files = "<br>".join(paths[:6]) + ("<br>…" if len(paths) > 6 else "")
        lines.append(f"| `{image}` | {len(paths)} | {files} |")

    lines += ["", "## Compose images", "", "| Image | Files |", "|---|---|"]
    for image, paths in report["compose_images"].items():
        lines.append(f"| `{image}` | {', '.join(paths)} |")

    lines += ["", "## GitHub Actions", "", "| Action | Files |", "|---|---|"]
    for action, paths in report["github_actions"].items():
        lines.append(f"| `{action}` | {', '.join(paths)} |")

    lines += ["", "_Generated by `scripts/report-versions.py`._", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument(
        "--platform-only",
        action="store_true",
        help="Exclude platform/labs, RangeBox, UbuntuBox, and RemnuxBox",
    )
    parser.add_argument("-o", "--output", help="Write to a file instead of stdout")
    args = parser.parse_args()

    report = collect(args.platform_only)
    text = json.dumps(report, indent=2, sort_keys=True) if args.json else markdown(report)
    if args.output:
        Path(args.output).write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
