#!/usr/bin/env python3
"""Build the namespaced workbook wiki tree into a persistent volume.

The container mounts the repository read-only at /repo and the wiki volume at
/out. Only the source needed for a docs build is copied into a writable temp
directory, so the host checkout is never modified and the image always builds
from the same pinned MkDocs toolchain.

Output layout:
  /out/index.html
  /out/range/<track>/...
  /out/reference/<manual>/...
  /out/course/<course>/...   (when tools/wiki-gen/courses.json has entries)
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

SRC = os.environ.get("WIKI_SOURCE_DIR", "/repo")
OUT = os.environ.get("WIKI_OUTPUT_DIR", "/out")

SOURCE_ITEMS = ("Workbook", "Manual-Lite", "tools/wiki-gen")
SOURCE_GLOBS = ("mkdocs*.yml", "wikis.yaml")
IGNORE = shutil.ignore_patterns(
    ".git",
    "__pycache__",
    "*.pyc",
    "node_modules",
    ".venv",
    "wiki",
    "wiki.prev",
)


def log(message: str) -> None:
    print(f"[wiki] {message}", flush=True)


def copy_source(work: str) -> None:
    for name in SOURCE_ITEMS:
        source = os.path.join(SRC, name)
        if not os.path.isdir(source):
            raise SystemExit(f"missing source directory: {source}")
        shutil.copytree(source, os.path.join(work, name), ignore=IGNORE)
    for pattern in SOURCE_GLOBS:
        for path in glob.glob(os.path.join(SRC, pattern)):
            if os.path.isfile(path):
                shutil.copy2(path, os.path.join(work, os.path.basename(path)))


def planned_sites(work: str) -> list[tuple[str, str, str]]:
    with open(os.path.join(work, "wikis.yaml"), encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}

    rows: list[tuple[str, str, str]] = []
    for slug, cfg in (manifest.get("tracks") or {}).items():
        if cfg.get("config"):
            rows.append(("range", slug, cfg["config"]))
    for slug, cfg in (manifest.get("reference") or {}).items():
        if cfg.get("config"):
            rows.append(("reference", slug, cfg["config"]))

    courses_path = os.path.join(work, "tools", "wiki-gen", "courses.json")
    if os.path.isfile(courses_path):
        try:
            with open(courses_path, encoding="utf-8") as handle:
                courses = json.load(handle) or []
        except (OSError, ValueError) as exc:
            raise SystemExit(f"cannot read courses.json: {exc}") from exc
        if isinstance(courses, list):
            for course in courses:
                if isinstance(course, dict) and course.get("slug") and course.get("config"):
                    rows.append(("course", course["slug"], course["config"]))
    return rows


def build(work: str, output: str) -> None:
    os.makedirs(os.path.join(output, "range"), exist_ok=True)
    os.makedirs(os.path.join(output, "reference"), exist_ok=True)
    os.makedirs(os.path.join(output, "course"), exist_ok=True)

    sites = planned_sites(work)
    if not sites:
        raise SystemExit("wikis.yaml did not define any buildable sites")

    for namespace, slug, config in sites:
        if not os.path.isfile(os.path.join(work, config)):
            raise SystemExit(f"missing MkDocs config for {namespace}/{slug}: {config}")
        destination = os.path.join(output, namespace, slug)
        log(f"building {namespace}/{slug} ({config})")
        subprocess.run(
            ["mkdocs", "build", "-f", config, "--site-dir", destination, "--clean"],
            cwd=work,
            check=True,
        )

    index = os.path.join(work, "tools", "wiki-gen", "generated", "index.html")
    if not os.path.isfile(index):
        raise SystemExit("wiki generator did not produce an index.html")
    shutil.copy2(index, os.path.join(output, "index.html"))
    log(f"built {len(sites)} site(s)")


def replace_output(staged: str) -> None:
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        path = os.path.join(OUT, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    for name in os.listdir(staged):
        shutil.move(os.path.join(staged, name), os.path.join(OUT, name))


def main() -> int:
    work = tempfile.mkdtemp(prefix="ocr-wiki-src-")
    staged = tempfile.mkdtemp(prefix="ocr-wiki-out-")
    try:
        log(f"copying source from {SRC}")
        copy_source(work)
        log("generating wiki routing metadata")
        subprocess.run(
            [
                sys.executable,
                "tools/wiki-gen/generate.py",
                "emit",
                "--out",
                "tools/wiki-gen/generated",
            ],
            cwd=work,
            check=True,
        )
        build(work, staged)
        replace_output(staged)
        log(f"published to {OUT}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(staged, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"wiki build failed: {exc}") from exc
