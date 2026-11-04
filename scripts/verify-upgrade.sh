#!/usr/bin/env bash
# Read-only preflight verification for an OpenCyberRange upgrade.
#
# This script never upgrades, restarts, or writes to the database. It checks
# that the repository, remote, containers, database, backup path, user export,
# and health endpoints are ready before the full upgrade script runs.
#
# Usage:
#   bash scripts/verify-upgrade.sh
#   bash scripts/verify-upgrade.sh --remote origin --branch main
#
# Exit codes: 0 = ready, 1 = one or more blocking failures.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$SOURCE_ROOT"
PLATFORM_DIR="$REPO_DIR/platform"
USER_TRANSFER="$SCRIPT_DIR/user_transfer.py"
TARGET_REPO=""
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/opencyberrange-backups}"
REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${GIT_BRANCH:-main}"
DB_USER="${DB_USER:-}"
DB_NAME="${DB_NAME:-}"
RANGEBOX_IMAGE="${RANGEBOX_IMAGE:-opencyberrange/rangebox:lite}"
UBUNTUBOX_IMAGE="${UBUNTUBOX_IMAGE:-opencyberrange/ubuntubox:latest}"
REMNUX_IMAGE="${REMNUX_IMAGE:-opencyberrange/remnuxbox:noble}"
RUNTIME_ONLY=false
PASS=0
FAIL=0
WARN=0

usage() {
  cat <<'EOF'
Usage: verify-upgrade.sh [options]

Options:
  --repo DIR          Existing OpenCyberRange deployment to verify (a Git
                      checkout with .env and docker-compose.yml at its root,
                      or platform/.env for the development layout)
  --remote NAME       Git remote to verify (default: origin, then the legacy
                      backup remote)
  --branch NAME       Git branch to verify (default: main)
  --backup-root DIR   Backup destination to check
  --db-user USER      PostgreSQL user (default: POSTGRES_USER from platform/.env)
  --db-name NAME      PostgreSQL database (default: POSTGRES_DB from platform/.env)
  --runtime-only      Skip Git/upgrade checks; check only runtime health, schema,
                      labs, images, and disk (use after an installation)
  -h, --help          Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) TARGET_REPO="${2:?--repo requires a value}"; shift 2 ;;
    --remote) REMOTE="${2:?--remote requires a value}"; shift 2 ;;
    --branch) BRANCH="${2:?--branch requires a value}"; shift 2 ;;
    --backup-root) BACKUP_ROOT="${2:?--backup-root requires a value}"; shift 2 ;;
    --db-user) DB_USER="${2:?--db-user requires a value}"; shift 2 ;;
    --db-name) DB_NAME="${2:?--db-name requires a value}"; shift 2 ;;
    --runtime-only) RUNTIME_ONLY=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

pass() { printf '[PASS] %s\n' "$*"; PASS=$((PASS + 1)); }
fail() { printf '[FAIL] %s\n' "$*" >&2; FAIL=$((FAIL + 1)); }
warn() { printf '[WARN] %s\n' "$*"; WARN=$((WARN + 1)); }

env_value() {
  local key="$1" file="$2"
  [[ -f "$file" ]] || return 0
  grep -E "^${key}=" "$file" | tail -1 | cut -d= -f2- \
    | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

docker_path() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s' "$1"
  fi
}

# Run git as the repository owner when started with sudo, so root does not
# trip Git's dubious-ownership check or create root-owned files.
repo_git() {
  if [[ "$(id -u)" -eq 0 && -n "${SUDO_USER:-}" ]]; then
    sudo -u "$SUDO_USER" \
      SSH_AUTH_SOCK="${SSH_AUTH_SOCK:-}" \
      GIT_SSH_COMMAND="${GIT_SSH_COMMAND:-}" \
      git -C "$REPO_DIR" "$@"
  else
    git -C "$REPO_DIR" "$@"
  fi
}

if [[ -n "$TARGET_REPO" ]]; then
  if [[ ! -d "$TARGET_REPO" ]]; then
    echo "deployment directory does not exist: $TARGET_REPO" >&2
    exit 2
  fi
  REPO_DIR="$(cd "$TARGET_REPO" && pwd)"
fi
# Installed deployments keep docker-compose.yml and .env at the checkout root
# and copy the code into backend/ and frontend/. Checkout deployments keep the
# compose files under platform/.
if [[ -f "$REPO_DIR/docker-compose.yml" && -f "$REPO_DIR/.env" ]]; then
  PLATFORM_DIR="$REPO_DIR"
else
  PLATFORM_DIR="$REPO_DIR/platform"
fi

if [[ "$RUNTIME_ONLY" == true ]]; then
  echo "OpenCyberRange post-install health check"
else
  echo "OpenCyberRange upgrade verification"
fi
echo "Repository: $REPO_DIR"
echo "Scripts:    $SCRIPT_DIR"
echo "Deployment: $PLATFORM_DIR"
echo

# ---------------------------------------------------------------------------
# Tooling and files
# ---------------------------------------------------------------------------

if command -v docker >/dev/null 2>&1; then
  pass "docker is installed"
else
  fail "docker is not installed or not on PATH"
fi

if docker compose version >/dev/null 2>&1; then
  pass "docker compose v2 is available"
else
  fail "docker compose v2 is not available"
fi

if command -v git >/dev/null 2>&1; then
  pass "git is installed"
else
  fail "git is not installed"
fi

if repo_git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  pass "repository is a git checkout"
else
  fail "not a git checkout: $REPO_DIR"
fi

if [[ -f "$PLATFORM_DIR/.env" ]]; then
  pass "deployment .env exists"
else
  fail "deployment .env is missing"
fi

if [[ -z "$DB_USER" ]]; then
  DB_USER="$(env_value POSTGRES_USER "$PLATFORM_DIR/.env")"
  DB_USER="${DB_USER:-labuser}"
fi
if [[ -z "$DB_NAME" ]]; then
  DB_NAME="$(env_value POSTGRES_DB "$PLATFORM_DIR/.env")"
  DB_NAME="${DB_NAME:-labdb}"
fi
pass "database target resolves to $DB_USER@$DB_NAME"

LABS_HOST_PATH_VALUE="$(env_value LABS_HOST_PATH "$PLATFORM_DIR/.env" | tr -d '\r')"
if [[ -z "$LABS_HOST_PATH_VALUE" ]]; then
  fail "LABS_HOST_PATH is empty in $PLATFORM_DIR/.env; set it to the absolute path of the labs directory"
fi
pass "LABS_HOST_PATH resolves to $LABS_HOST_PATH_VALUE"

if [[ -f "$USER_TRANSFER" ]]; then
  pass "user transfer utility exists"
else
  fail "scripts/user_transfer.py is missing"
fi

if [[ -f "$SCRIPT_DIR/purge_erased_accounts.py" ]]; then
  pass "erasure restore-purge utility exists"
else
  fail "scripts/purge_erased_accounts.py is missing"
fi

if [[ -f "$SOURCE_ROOT/platform/backend/app/services/erasure_ledger.py" ]]; then
  pass "erasure suppression ledger module exists"
else
  fail "platform/backend/app/services/erasure_ledger.py is missing"
fi

if [[ -f "$SCRIPT_DIR/upgrade-from-backup.sh" ]]; then
  pass "upgrade script exists"
else
  fail "scripts/upgrade-from-backup.sh is missing"
fi

if [[ -f "$SCRIPT_DIR/prebuild-labs.sh" ]]; then
  pass "lab prebuild script exists"
else
  fail "scripts/prebuild-labs.sh is missing"
fi

LAB_COUNT="$(find "$SOURCE_ROOT/platform/labs" -type f -name lab.yaml 2>/dev/null | wc -l | tr -d '[:space:]')"
if [[ "$LAB_COUNT" =~ ^[0-9]+$ ]] && (( LAB_COUNT > 0 )); then
  pass "found $LAB_COUNT lab definitions"
else
  fail "no lab definitions found under platform/labs"
fi

if [[ -f "$SCRIPT_DIR/prebuild-labs.sh" ]]; then
  PREBUILD_COUNT="$(bash "$SCRIPT_DIR/prebuild-labs.sh" --dry-run 2>/dev/null \
    | grep -cE '^[[:space:]]*\[[0-9]+/[0-9]+\].*Would build:')"
  if [[ "$PREBUILD_COUNT" =~ ^[0-9]+$ ]] && (( PREBUILD_COUNT > 0 )); then
    if [[ "$LAB_COUNT" =~ ^[0-9]+$ ]] && (( PREBUILD_COUNT != LAB_COUNT )); then
      warn "lab prebuild script found $PREBUILD_COUNT labs but $LAB_COUNT lab definitions exist"
    else
      pass "lab prebuild script discovered $PREBUILD_COUNT buildable labs"
    fi
  else
    fail "lab prebuild script did not discover any buildable labs"
  fi
fi

for box in RangeBox UbuntuBox RemnuxBox; do
  if [[ -f "$SOURCE_ROOT/$box/Dockerfile" ]]; then
    pass "$box build source exists"
  else
    fail "$box/Dockerfile is missing"
  fi
done

for image in "$RANGEBOX_IMAGE" "$UBUNTUBOX_IMAGE" "$REMNUX_IMAGE"; do
  if docker image inspect "$image" >/dev/null 2>&1; then
    pass "RangeBox image is present: $image"
  else
    warn "RangeBox image is not built yet; the upgrade will build it: $image"
  fi
done

# ---------------------------------------------------------------------------
# Compose
# ---------------------------------------------------------------------------

COMPOSE=()
if [[ -f "$PLATFORM_DIR/docker-compose.yml" ]]; then
  COMPOSE=(docker compose -f "$(docker_path "$PLATFORM_DIR/docker-compose.yml")")
elif [[ -f "$PLATFORM_DIR/docker-compose.prod.yml" ]]; then
  COMPOSE=(docker compose -f "$(docker_path "$PLATFORM_DIR/docker-compose.prod.yml")")
fi
if [[ ${#COMPOSE[@]} -gt 0 && -f "$PLATFORM_DIR/docker-compose.override.yml" ]]; then
  COMPOSE+=(-f "$(docker_path "$PLATFORM_DIR/docker-compose.override.yml")")
fi
# Optional operator layer. Existing deployments use it to pin a named volume
# (for example adopting the Postgres volume that already holds the data)
# without editing tracked compose files. Keep it last so it wins.
if [[ ${#COMPOSE[@]} -gt 0 && -f "$PLATFORM_DIR/docker-compose.adopt.yml" ]]; then
  COMPOSE+=(-f "$(docker_path "$PLATFORM_DIR/docker-compose.adopt.yml")")
fi
compose() { "${COMPOSE[@]}" "$@"; }
# Git Bash rewrites absolute container paths such as /tmp/x into Windows paths
# before Docker sees them. Disable that conversion for exec/cp arguments.
compose_in() { MSYS_NO_PATHCONV=1 "${COMPOSE[@]}" "$@"; }

if [[ ${#COMPOSE[@]} -eq 0 ]]; then
  fail "no docker-compose.yml or docker-compose.prod.yml found"
else
  if compose config --quiet >/dev/null 2>&1; then
    pass "docker compose configuration is valid"
  else
    fail "docker compose configuration is invalid"
  fi
fi

for svc in db backend frontend; do
  if [[ ${#COMPOSE[@]} -gt 0 ]] && compose ps -q "$svc" 2>/dev/null | grep -q .; then
    pass "$svc container is running"
  else
    fail "$svc container is not running"
  fi
done

if [[ ${#COMPOSE[@]} -gt 0 ]]; then
  if compose_in exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    pass "PostgreSQL is accepting connections"
  else
    fail "PostgreSQL is not accepting connections for $DB_USER@$DB_NAME"
  fi
fi

# ---------------------------------------------------------------------------
# Git remote and upgrade path
# ---------------------------------------------------------------------------

if [[ "$RUNTIME_ONLY" == false ]]; then
  if repo_git remote get-url "$REMOTE" >/dev/null 2>&1; then
    pass "git remote '$REMOTE' exists"
  else
    if [[ "$REMOTE" == "origin" ]] && repo_git remote get-url backup >/dev/null 2>&1; then
      warn "remote 'origin' not found; using the legacy 'backup' remote"
      REMOTE=backup
      pass "git remote 'backup' exists"
    else
      fail "git remote '$REMOTE' does not exist"
    fi
  fi

  DIRTY="$(repo_git status --porcelain --untracked-files=no 2>/dev/null || true)"
  if [[ -z "$DIRTY" ]]; then
    pass "working tree has no modified tracked files"
  else
    fail "working tree has uncommitted tracked changes; commit or stash them first"
  fi

  if repo_git fetch --quiet "$REMOTE" \
      "+refs/heads/$BRANCH:refs/remotes/$REMOTE/$BRANCH" >/dev/null 2>&1; then
    pass "fetched $REMOTE/$BRANCH"
    LOCAL_SHA="$(repo_git rev-parse HEAD)"
    REMOTE_SHA="$(repo_git rev-parse "$REMOTE/$BRANCH" 2>/dev/null || true)"
    if [[ -z "$REMOTE_SHA" ]]; then
      fail "could not resolve $REMOTE/$BRANCH after fetch"
    elif [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
      pass "checkout is already at $REMOTE/$BRANCH ($LOCAL_SHA)"
    elif repo_git merge-base --is-ancestor "$LOCAL_SHA" "$REMOTE_SHA"; then
      pass "checkout can fast-forward to $REMOTE/$BRANCH"
    else
      fail "checkout cannot fast-forward to $REMOTE/$BRANCH; resolve divergence first"
    fi
  else
    fail "could not fetch $REMOTE/$BRANCH (try: git -C $REPO_DIR fetch $REMOTE $BRANCH)"
  fi
fi

# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------

if [[ ${#COMPOSE[@]} -gt 0 ]]; then
  if compose_in exec -T backend curl -fsS http://localhost:8000/health 2>/dev/null | grep -q '"status":"healthy"'; then
    pass "backend health endpoint reports healthy"
  else
    fail "backend health endpoint is not healthy"
  fi
fi

if command -v curl >/dev/null 2>&1; then
  if curl -fsS -o /dev/null http://localhost/ 2>/dev/null; then
    pass "frontend responds on http://localhost/"
  else
    fail "frontend does not respond on http://localhost/"
  fi
  if curl -kfsS -o /dev/null https://localhost/ 2>/dev/null; then
    pass "frontend responds on https://localhost/"
  else
    warn "frontend HTTPS check failed (self-signed or HTTP-only is possible)"
  fi
else
  warn "curl is not installed; frontend HTTP checks skipped"
fi

# ---------------------------------------------------------------------------
# Backup path and dump
# ---------------------------------------------------------------------------

if [[ "$RUNTIME_ONLY" == false ]]; then
  if mkdir -p "$BACKUP_ROOT" 2>/dev/null && [[ -w "$BACKUP_ROOT" ]]; then
    pass "backup root is writable: $BACKUP_ROOT"
  else
    fail "backup root is not writable: $BACKUP_ROOT"
  fi

  TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ocr-verify.XXXXXX" 2>/dev/null || true)"
  if [[ -z "$TMP_DIR" ]]; then
    warn "could not create a temporary directory; dump test skipped"
  else
    if [[ ${#COMPOSE[@]} -gt 0 ]] && compose_in exec -T db pg_dump \
        -U "$DB_USER" -d "$DB_NAME" --schema-only --no-owner --no-privileges -Fc \
        > "$TMP_DIR/schema.dump" 2>/dev/null && [[ -s "$TMP_DIR/schema.dump" ]]; then
      pass "pg_dump schema test succeeded"
    else
      fail "pg_dump schema test failed"
    fi

    if [[ -f "$USER_TRANSFER" && ${#COMPOSE[@]} -gt 0 ]]; then
      compose_in cp "$(docker_path "$USER_TRANSFER")" \
        backend:/tmp/ocr-verify-user-transfer.py >/dev/null 2>&1 || true
      if compose_in exec -T backend python /tmp/ocr-verify-user-transfer.py \
          export -o /tmp/ocr-verify-users.json >/dev/null 2>&1; then
        if compose_in cp backend:/tmp/ocr-verify-users.json "$(docker_path "$TMP_DIR/users.json")" >/dev/null 2>&1; then
          if compose_in exec -T backend python -c \
              "import json; d=json.load(open('/tmp/ocr-verify-users.json')); assert d.get('format')=='opencyberrange-users'; assert isinstance(d.get('users'), list); print(len(d['users']))" \
              >/dev/null 2>&1; then
            pass "user export test succeeded"
          else
            fail "user export payload is invalid"
          fi
        else
          fail "could not copy the user export out of the backend"
        fi
        if compose_in exec -T backend python /tmp/ocr-verify-user-transfer.py \
            import /tmp/ocr-verify-users.json --dry-run >/dev/null 2>&1; then
          pass "user import dry-run succeeded (no writes)"
        else
          fail "user import dry-run failed"
        fi
      else
        fail "user export failed"
      fi
      compose_in exec -T backend rm -f \
        /tmp/ocr-verify-user-transfer.py /tmp/ocr-verify-users.json >/dev/null 2>&1 || true
    fi
    rm -rf "$TMP_DIR"
  fi
fi

if [[ ${#COMPOSE[@]} -gt 0 ]]; then
  USER_COUNT="$(compose_in exec -T db psql -U "$DB_USER" -d "$DB_NAME" \
    -tAc "SELECT count(*) FROM users;" 2>/dev/null | tr -d '[:space:]')"
  if [[ "$USER_COUNT" =~ ^[0-9]+$ ]]; then
    pass "users table is readable ($USER_COUNT accounts)"
  else
    fail "could not read the users table"
  fi

  SCHEMA_OUT="$(compose_in exec -T backend python - 2>/dev/null <<'PY'
import sys
from sqlalchemy import inspect
from app.database import engine, Base
import app.models  # noqa: F401 - register all tables

insp = inspect(engine)
missing = []
for table in Base.metadata.sorted_tables:
    if not insp.has_table(table.name):
        missing.append("table:" + table.name)
        continue
    existing = {c["name"] for c in insp.get_columns(table.name)}
    for column in table.columns:
        if column.name not in existing:
            missing.append(table.name + "." + column.name)
if missing:
    print("\n".join(missing))
    sys.exit(1)
print("ok")
PY
)"
  if [[ $? -eq 0 && "$SCHEMA_OUT" == "ok" ]]; then
    pass "database schema matches the application models"
  else
    MISSING_PREVIEW="$(printf '%s' "$SCHEMA_OUT" | head -5 | tr '\n' ' ')"
    fail "database schema is missing: ${MISSING_PREVIEW:-unknown (could not inspect)}"
  fi
fi

if command -v df >/dev/null 2>&1; then
  AVAIL_KB="$(df -Pk "$BACKUP_ROOT" 2>/dev/null | awk 'NR==2 {print $4}')"
  if [[ -n "$AVAIL_KB" && "$AVAIL_KB" =~ ^[0-9]+$ ]]; then
    if (( AVAIL_KB >= 20971520 )); then
      pass "backup disk has at least 20 GiB free for lab and RangeBox rebuilds"
    elif (( AVAIL_KB >= 10485760 )); then
      warn "backup disk has 10-20 GiB free; a full lab/RangeBox rebuild may be tight"
    else
      fail "backup disk has less than 10 GiB free; full lab/RangeBox rebuild will fail"
    fi
  fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo
echo "Summary: $PASS passed, $FAIL failed, $WARN warning(s)"
if (( FAIL > 0 )); then
  echo "Not ready for upgrade. Fix the failures above." >&2
  exit 1
fi

if [[ "$RUNTIME_ONLY" == true ]]; then
  echo "Runtime checks passed."
else
  echo "Verification passed. You can run:"
  if [[ -n "$TARGET_REPO" ]]; then
    echo "  sudo bash $SCRIPT_DIR/upgrade-from-backup.sh --repo '$REPO_DIR' --remote $REMOTE --branch $BRANCH"
  else
    echo "  sudo bash scripts/upgrade-from-backup.sh --remote $REMOTE --branch $BRANCH"
  fi
fi
exit 0
