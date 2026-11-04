#!/usr/bin/env python3
"""Check internal documentation links and MkDocs navigation.

Default mode checks local files only, which is safe for pull-request CI. Pass
``--external`` to also probe http(s) links (slow, network-dependent; 403 and
429 are treated as reachable because many vendors block bots).

Usage:
    python3 scripts/check-links.py
    python3 scripts/check-links.py Manual-Lite docs/lite platform/labs
    python3 scripts/check-links.py --external --timeout 15
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs PyYAML explicitly
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATHS = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "Manual-Lite",
    "docs",
    "Workbook",
    "platform/labs",
]


class _DocsLoader(yaml.SafeLoader):
    """SafeLoader that tolerates MkDocs' !!python/name: tags."""


def _construct_python_tag(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


_DocsLoader.add_multi_constructor("tag:yaml.org,2002:python/", _construct_python_tag)

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "ftp:", "data:")
_EXTERNAL_CACHE: dict[str, str | None] = {}


def slugify(heading: str) -> str:
    """Approximate the slug GitHub/MkDocs generate for a heading."""
    text = re.sub(r"<[^>]+>", "", heading)
    text = text.replace("`", "")
    text = re.sub(r"[*_~]", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def markdown_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return files


def strip_code(text: str) -> str:
    """Blank fenced code blocks and inline code so examples are not checked."""
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            lines.append("")
            continue
        lines.append("" if in_fence else re.sub(r"`[^`]*`", "", line))
    return "\n".join(lines)


def anchors_for(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        slug = slugify(match.group(2))
        if not slug:
            continue
        seen = counts.get(slug, 0)
        anchors.add(slug if seen == 0 else f"{slug}-{seen}")
        counts[slug] = seen + 1
    return anchors


def check_external(url: str, timeout: float) -> str | None:
    if url in _EXTERNAL_CACHE:
        return _EXTERNAL_CACHE[url]
    result = _probe_external(url, timeout)
    _EXTERNAL_CACHE[url] = result
    return result


def _probe_external(url: str, timeout: float) -> str | None:
    request = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "OpenCyberRange-LinkCheck/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return None if response.status < 400 else f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 429):
            # Bots are commonly blocked; try GET before giving up.
            if exc.code == 405:
                return _external_get(url, timeout)
            return None
        return f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return str(getattr(exc, "reason", exc))


def _external_get(url: str, timeout: float) -> str | None:
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "OpenCyberRange-LinkCheck/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return None if response.status < 400 else f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        return None if exc.code in (403, 405, 429) else f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return str(getattr(exc, "reason", exc))


def resolve_target(source: Path, target: str) -> tuple[Path | None, str]:
    """Return (absolute path, anchor) for a relative link target."""
    parsed = urllib.parse.urlsplit(target)
    anchor = parsed.fragment
    path = urllib.parse.unquote(parsed.path)
    if not path:
        return source, anchor
    candidate = (source.parent / path).resolve()
    if candidate.is_dir():
        index = candidate / "index.md"
        if index.exists():
            return index, anchor
        readme = candidate / "README.md"
        if readme.exists():
            return readme, anchor
    return candidate, anchor


def check_file(path: Path, anchors: bool, external: bool, timeout: float) -> list[str]:
    problems: list[str] = []
    text = strip_code(path.read_text(encoding="utf-8", errors="replace"))
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith("#") or target.lower().startswith(SKIP_SCHEMES):
            if external and target.lower().startswith(("http://", "https://")):
                error = check_external(target, timeout)
                if error:
                    problems.append(f"{path}: external link {target} -> {error}")
            continue
        if SCHEME_RE.match(target) or target.startswith("/") or "{{" in target:
            continue

        resolved, anchor = resolve_target(path, target)
        if resolved is None:
            continue
        if not resolved.exists():
            problems.append(f"{path}: missing target {target}")
            continue
        if anchors and anchor and resolved.suffix.lower() == ".md":
            if anchor not in anchors_for(resolved):
                problems.append(f"{path}: missing anchor #{anchor} in {target}")
    return problems


def check_mkdocs_nav(config_path: Path) -> list[str]:
    problems: list[str] = []
    try:
        config = yaml.load(config_path.read_text(encoding="utf-8"), Loader=_DocsLoader) or {}
    except yaml.YAMLError as exc:
        return [f"{config_path}: invalid YAML: {exc}"]

    docs_dir = config_path.parent / (config.get("docs_dir") or "docs")
    if not docs_dir.is_dir():
        return [f"{config_path}: docs_dir does not exist: {docs_dir}"]

    def walk(node) -> None:
        if isinstance(node, str):
            if node.endswith(".md") and not (docs_dir / node).is_file():
                problems.append(f"{config_path}: nav entry missing: {node}")
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, dict):
            for child in node.values():
                walk(child)

    walk(config.get("nav"))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Files or directories to check")
    parser.add_argument(
        "--external",
        action="store_true",
        help="Also probe external http(s) links (network required)",
    )
    parser.add_argument(
        "--no-anchors",
        action="store_true",
        help="Only check that target files exist, not #anchors",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="External timeout")
    parser.add_argument(
        "--mkdocs",
        action="store_true",
        help="Check every mkdocs-*.yml nav entry",
    )
    args = parser.parse_args()

    targets = [Path(p) for p in args.paths] if args.paths else [
        REPO_ROOT / p for p in DEFAULT_PATHS
    ]
    targets = [t if t.is_absolute() else (Path.cwd() / t) for t in targets]

    problems: list[str] = []
    files = markdown_files(targets)
    for path in files:
        problems.extend(
            check_file(path, anchors=not args.no_anchors, external=args.external, timeout=args.timeout)
        )

    if args.mkdocs:
        for config in sorted(REPO_ROOT.glob("mkdocs-*.yml")):
            problems.extend(check_mkdocs_nav(config))

    if problems:
        print(f"Found {len(problems)} documentation link problem(s):\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(f"Checked {len(files)} Markdown file(s); no broken links found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
