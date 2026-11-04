#!/usr/bin/env bash
# Verify lab compose files, stable images, and workbook links.
#
# Run after scripts/prebuild-labs.sh and scripts/build-wiki.sh. The script is
# deliberately read-only: it starts no containers.
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABS_DIR="$REPO_DIR/platform/labs"
HASH_HELPER="$REPO_DIR/scripts/lab_build_hash.py"
FRONTEND_CONTAINER="${FRONTEND_CONTAINER:-ocr-frontend}"
DB_CONTAINER="${DB_CONTAINER:-ocr-db}"
ERRORS=0
WARNINGS=0

fail() { echo "ERROR: $*"; ERRORS=$((ERRORS + 1)); }
warn() { echo "WARN:  $*"; WARNINGS=$((WARNINGS + 1)); }

echo "[*] checking lab compose files"
while IFS= read -r -d '' compose; do
    lab_dir="$(dirname "$compose")"
    slug="$(basename "$lab_dir")"

    if ! (cd "$lab_dir" && docker compose -p verify_lab config -q >/dev/null 2>&1); then
        fail "$slug: docker compose config failed"
    fi

    if grep -nE '^[[:space:]]*-[[:space:]]+/[^:]*:(size|mode):' "$compose" >/dev/null 2>&1; then
        fail "$slug: invalid tmpfs option (use size= / mode=, not size: / mode:)"
    fi

    meta="$(python3 "$HASH_HELPER" "$lab_dir" 2>/dev/null || true)"
    if [ -z "$meta" ]; then
        fail "$slug: could not read compose services"
        continue
    fi
    services="$(printf '%s' "$meta" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin)["services"]))' 2>/dev/null || true)"
    for svc in $services; do
        if ! docker image inspect "ocr-lab/${slug}-${svc}:latest" >/dev/null 2>&1; then
            fail "$slug: missing stable image ocr-lab/${slug}-${svc}:latest"
        fi
    done
done < <(find "$LABS_DIR" -mindepth 3 -maxdepth 3 -name docker-compose.yml -print0)

echo "[*] checking workbook links in the running frontend"
if docker inspect "$FRONTEND_CONTAINER" >/dev/null 2>&1; then
    while IFS='|' read -r slug workbook; do
        [ -n "$workbook" ] || continue
        path="/usr/share/nginx/wiki/${workbook#/}"
        if ! docker exec "$FRONTEND_CONTAINER" test -f "$path/index.html" >/dev/null 2>&1; then
            case "$workbook" in
                wiki/course/*)
                    warn "$slug: course workbook not built ($workbook)"
                    ;;
                *)
                    fail "$slug: workbook missing ($workbook)"
                    ;;
            esac
        fi
    done < <(docker exec "$DB_CONTAINER" psql -U labuser -d labdb -tAc \
        "SELECT slug, workbook FROM labs WHERE workbook IS NOT NULL AND workbook <> '';" 2>/dev/null)
else
    warn "frontend container $FRONTEND_CONTAINER is not running; skipped workbook links"
fi

echo ""
echo "Summary: ${ERRORS} error(s), ${WARNINGS} warning(s)"
[ "$ERRORS" -eq 0 ]
