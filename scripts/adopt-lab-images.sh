#!/usr/bin/env bash
# Adopt images produced by the old prebuild tags into the stable ocr-lab/* tags.
#
# One-time migration for hosts that already ran prebuild-labs.sh before the
# stable-tag change. It does not build anything: it copies existing
# prebuild-<slug>-<service> or <slug>-<service> images to
# ocr-lab/<slug>-<service>:latest and records their content hash in the
# manifest so the next --changed run can skip them.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABS_DIR="$REPO_DIR/platform/labs"
HASH_HELPER="$REPO_DIR/scripts/lab_build_hash.py"
MANIFEST_FILE="$REPO_DIR/scripts/.lab-build-manifest.json"
MISSING=0

record() {
    python3 - "$MANIFEST_FILE" "$1" "$2" "$3" <<'PY'
import datetime, json, sys
path, slug, digest, services = sys.argv[1:5]
try:
    data = json.load(open(path, encoding="utf-8"))
except Exception:
    data = {"version": 1, "labs": {}}
data.setdefault("labs", {})[slug] = {
    "hash": digest,
    "services": services.split(),
    "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY
}

while IFS= read -r -d '' compose; do
    lab_dir="$(dirname "$compose")"
    slug="$(basename "$lab_dir")"
    meta="$(python3 "$HASH_HELPER" "$lab_dir")"
    digest="$(printf '%s' "$meta" | python3 -c 'import json,sys; print(json.load(sys.stdin)["hash"])')"
    services="$(printf '%s' "$meta" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin)["services"]))')"

    lab_ok=true
    for svc in $services; do
        found=""
        for candidate in "prebuild-${slug}-${svc}:latest" "${slug}-${svc}:latest"; do
            if docker image inspect "$candidate" >/dev/null 2>&1; then
                found="$candidate"
                break
            fi
        done
        if [ -z "$found" ]; then
            echo "MISSING ${slug}/${svc}"
            lab_ok=false
            MISSING=$((MISSING + 1))
            continue
        fi
        docker tag "$found" "ocr-lab/${slug}-${svc}:latest" >/dev/null
        docker tag "$found" "ocr-lab/${slug}-${svc}:${digest}" >/dev/null
        echo "ADOPTED ${slug}/${svc} <- ${found}"
    done

    if [ "$lab_ok" = true ]; then
        record "$slug" "$digest" "$services"
    fi
done < <(find "$LABS_DIR" -mindepth 3 -maxdepth 3 -name docker-compose.yml -print0)

echo ""
echo "Missing images: ${MISSING}"
[ "$MISSING" -eq 0 ]
