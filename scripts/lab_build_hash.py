#!/usr/bin/env python3
"""Return a stable content hash for a lab image build.

The hash covers the lab directory (compose file, Dockerfiles, app files) and
every compose build context, so a change to a shared context invalidates all
labs that use it. Output is JSON: {"hash": "...", "services": ["..."]}.

PyYAML is used when it is installed, with a small line parser as a fallback so
the prebuild script also works on a host that only has the stdlib.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "wiki", "wiki.prev", "dist"}
SKIP_SUFFIXES = (".pyc", ".pyo")


def load_services(compose_path: str) -> dict:
    try:
        import yaml  # type: ignore

        with open(compose_path, encoding="utf-8") as handle:
            compose = yaml.safe_load(handle) or {}
        return compose.get("services") or {}
    except Exception:
        pass

    services: dict[str, dict] = {}
    current: str | None = None
    with open(compose_path, encoding="utf-8") as handle:
        for line in handle:
            service = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
            if service:
                current = service.group(1)
                services[current] = {}
                continue
            if current is None:
                continue
            build = re.match(r"^    build:\s*(.*)$", line)
            if build:
                value = build.group(1).strip()
                services[current]["build"] = value or {}
                continue
            context = re.match(r"^      context:\s*[\"']?([^\"']+?)[\"']?\s*$", line)
            if context and isinstance(services[current].get("build"), dict):
                services[current]["build"]["context"] = context.group(1)
    return services


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: lab_build_hash.py <lab-dir>")
    lab_dir = os.path.abspath(sys.argv[1])
    compose_path = os.path.join(lab_dir, "docker-compose.yml")
    if not os.path.isfile(compose_path):
        raise SystemExit(f"missing compose file: {compose_path}")

    services = load_services(compose_path)

    roots = [lab_dir]
    built_services: list[str] = []
    for name, cfg in services.items():
        if not isinstance(cfg, dict) or not cfg.get("build"):
            continue
        built_services.append(name)
        build = cfg.get("build")
        context = build.get("context") if isinstance(build, dict) else build
        roots.append(os.path.normpath(os.path.join(lab_dir, context or ".")))

    seen_files: set[str] = set()
    digest = hashlib.sha256()
    for root in sorted(set(roots)):
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for filename in sorted(filenames):
                if filename.endswith(SKIP_SUFFIXES):
                    continue
                path = os.path.join(dirpath, filename)
                if path in seen_files:
                    continue
                seen_files.add(path)
                rel = os.path.relpath(path, root)
                digest.update(rel.encode("utf-8", "surrogateescape"))
                digest.update(b"\0")
                with open(path, "rb") as handle:
                    for chunk in iter(lambda: handle.read(65536), b""):
                        digest.update(chunk)

    print(json.dumps({"hash": digest.hexdigest(), "services": sorted(built_services)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
