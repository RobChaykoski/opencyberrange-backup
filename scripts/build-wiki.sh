#!/usr/bin/env bash
# Build the workbook wiki into the compose wiki_data volume.
#
# The builder image is pinned to the same MkDocs/Material versions as the docs
# toolchain. The repository is mounted read-only; only the output volume is
# written. Run this after changing Workbook/, wikis.yaml, or mkdocs-*.yml.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLATFORM_DIR="$REPO_DIR/platform"

if [ ! -f "$PLATFORM_DIR/.env" ]; then
    echo "error: $PLATFORM_DIR/.env is required" >&2
    exit 1
fi

cd "$PLATFORM_DIR"
COMPOSE=(docker compose --env-file .env)
if [ -n "${COMPOSE_PROJECT_NAME:-}" ]; then
    COMPOSE+=(-p "$COMPOSE_PROJECT_NAME")
fi
COMPOSE+=(-f docker-compose.prod.yml)
[ -f docker-compose.adopt.yml ] && COMPOSE+=(-f docker-compose.adopt.yml)
[ -f docker-compose.override.yml ] && COMPOSE+=(-f docker-compose.override.yml)
COMPOSE+=(--profile tools run --rm wiki-builder)

echo "[*] building workbook wiki into the wiki_data volume"
"${COMPOSE[@]}"
