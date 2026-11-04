#!/usr/bin/env bash
# Build and verify deployment assets.
#
#   build-assets.sh wiki     build the workbook wiki volume
#   build-assets.sh labs     prebuild new/changed lab images
#   build-assets.sh verify   validate compose files, images, and workbook links
#   build-assets.sh all      all of the above (default)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-all}"

case "$ACTION" in
    wiki)
        "$REPO_DIR/scripts/build-wiki.sh"
        ;;
    labs)
        "$REPO_DIR/scripts/prebuild-labs.sh" --changed
        ;;
    verify)
        "$REPO_DIR/scripts/verify-lab-builds.sh"
        ;;
    all)
        "$REPO_DIR/scripts/build-wiki.sh"
        "$REPO_DIR/scripts/prebuild-labs.sh" --changed
        "$REPO_DIR/scripts/verify-lab-builds.sh"
        ;;
    *)
        echo "usage: $0 [wiki|labs|verify|all]" >&2
        exit 1
        ;;
esac
