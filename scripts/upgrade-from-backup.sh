#!/usr/bin/env bash
# Upgrade an OpenCyberRange server from the configured Git remote.
#
# The historical "from-backup" file name is retained so existing runbooks and
# deployed copies keep working.
#
# The script:
#   1. backs up the database, users, .env, compose files, and certificates
#   2. fast-forwards the checkout from the selected remote/branch
#   3. rebuilds and recreates the backend and frontend
#   4. seeds the curriculum and discovers new labs
#   5. merges the backed-up users into the upgraded database
#   6. verifies the backend and frontend health
#
# Usage:
#   sudo bash scripts/upgrade-from-backup.sh
#   sudo bash scripts/upgrade-from-backup.sh --remote origin --update-users
#   sudo bash scripts/upgrade-from-backup.sh --help
#
# The user export contains password hashes. The backup directory is created
# with mode 700 and should be deleted after a successful upgrade.

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$SOURCE_ROOT"
PLATFORM_DIR="$REPO_DIR/platform"
USER_TRANSFER="$SCRIPT_DIR/user_transfer.py"
TARGET_REPO=""
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/opencyberrange-backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
ERASURE_LEDGER_PATH="${ERASURE_LEDGER_PATH:-/workbook/erasure-ledger.jsonl}"
REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${GIT_BRANCH:-main}"
DB_USER="${DB_USER:-}"
DB_NAME="${DB_NAME:-}"
RANGEBOX_IMAGE="${RANGEBOX_IMAGE:-opencyberrange/rangebox:lite}"
UBUNTUBOX_IMAGE="${UBUNTUBOX_IMAGE:-opencyberrange/ubuntubox:latest}"
REMNUX_IMAGE="${REMNUX_IMAGE:-opencyberrange/remnuxbox:noble}"
UPDATE_USERS=false
SKIP_USERS=false
SKIP_DISCOVERY=false
SKIP_VERIFY=false
SKIP_RANGEBOX=false
PREBUILD_LABS=true
PREBUILD_PARALLEL="${PREBUILD_PARALLEL:-1}"
CURRENT_STEP="preflight"
BACKUP_DIR=""

usage() {
  cat <<'EOF'
Usage: upgrade-from-backup.sh [options]

Options:
  --repo DIR            Existing OpenCyberRange deployment to upgrade (a Git
                        checkout with .env and docker-compose.yml at its root,
                        or platform/.env for the development layout)
  --remote NAME         Git remote to upgrade from (default: origin, then the
                        legacy backup remote)
  --branch NAME         Git branch to upgrade to (default: main)
  --backup-root DIR     Where to create the timestamped backup
  --db-user USER        PostgreSQL user (default: POSTGRES_USER from platform/.env)
  --db-name NAME        PostgreSQL database (default: POSTGRES_DB from platform/.env)
  --update-users        Overwrite existing users from the backup export
  --skip-users          Do not export or merge users (database backup still runs)
  --skip-discovery      Do not reseed curriculum or discover labs
  --skip-labs           Do not rebuild all lab images (definitions are still refreshed)
  --skip-rangebox       Do not rebuild Kali, Ubuntu, and REMnux RangeBox images
  --skip-verify         Skip the read-only preflight verification
  --prebuild-parallel N Build N lab images concurrently (default: 1)
  --backup-retention-days N
                        Delete completed ocr-* backups older than N days after
                        a successful upgrade (default: 30; 0 disables)
  -h, --help            Show this help

By default the upgrade refreshes curriculum/lab definitions, rebuilds every lab
image, and rebuilds the Kali, Ubuntu, and REMnux RangeBox images. Lab image
prebuilds can take a long time and need significant disk space; use --skip-labs
or --skip-rangebox for a code-only upgrade.

Environment overrides:
  BACKUP_ROOT, BACKUP_RETENTION_DAYS, ERASURE_LEDGER_PATH, GIT_REMOTE,
  GIT_BRANCH, DB_USER, DB_NAME, PREBUILD_PARALLEL
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
    --update-users) UPDATE_USERS=true; shift ;;
    --skip-users) SKIP_USERS=true; shift ;;
    --skip-discovery) SKIP_DISCOVERY=true; shift ;;
    --skip-labs) PREBUILD_LABS=false; shift ;;
    --skip-rangebox) SKIP_RANGEBOX=true; shift ;;
    --skip-verify) SKIP_VERIFY=true; shift ;;
    --prebuild-parallel) PREBUILD_PARALLEL="${2:?--prebuild-parallel requires a value}"; shift 2 ;;
    --backup-retention-days) BACKUP_RETENTION_DAYS="${2:?--backup-retention-days requires a value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

log() { printf '\n[*] %s\n' "$*"; }
warn() { printf '[!] %s\n' "$*" >&2; }
fail() { printf '[x] %s\n' "$*" >&2; exit 1; }

on_error() {
  local code=$?
  printf '\n[x] Upgrade failed during: %s\n' "$CURRENT_STEP" >&2
  if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
    printf '[x] Backup is at: %s\n' "$BACKUP_DIR" >&2
    printf '[x] Restore instructions are in: %s/README.txt\n' "$BACKUP_DIR" >&2
  fi
  exit "$code"
}
trap on_error ERR

env_value() {
  local key="$1" file="$2"
  [[ -f "$file" ]] || return 0
  grep -E "^${key}=" "$file" | tail -1 | cut -d= -f2- \
    | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

# Older .env files can have an empty LABS_HOST_PATH. Docker then expands the
# mount to ":/labs:ro" and fails with "empty section between colons" before the
# backup step even starts. Derive the absolute path instead of making the
# operator debug Compose.
ensure_labs_host_path() {
  local env_file="$PLATFORM_DIR/.env"
  [[ -f "$env_file" ]] || return 0

  local current
  current="$(env_value LABS_HOST_PATH "$env_file" | tr -d '\r')"
  [[ -n "$current" ]] && return 0

  local labs_dir=""
  if [[ -d "$PLATFORM_DIR/labs" ]]; then
    labs_dir="$(cd "$PLATFORM_DIR/labs" && pwd)"
  elif [[ -d "$REPO_DIR/platform/labs" ]]; then
    labs_dir="$(cd "$REPO_DIR/platform/labs" && pwd)"
  else
    warn "LABS_HOST_PATH is empty in $env_file and no labs directory was found"
    return 0
  fi

  if grep -q '^LABS_HOST_PATH=' "$env_file"; then
    sed -i "s|^LABS_HOST_PATH=.*|LABS_HOST_PATH=$labs_dir|" "$env_file"
  else
    printf '\nLABS_HOST_PATH=%s\n' "$labs_dir" >> "$env_file"
  fi
  log "Set LABS_HOST_PATH=$labs_dir in $env_file"
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
  [[ -d "$TARGET_REPO" ]] || fail "deployment directory does not exist: $TARGET_REPO"
  REPO_DIR="$(cd "$TARGET_REPO" && pwd)"
fi
# Installed deployments keep docker-compose.yml and .env at the checkout root
# and copy the code into backend/ and frontend/. Checkout deployments keep the
# compose files under platform/.
if [[ -f "$REPO_DIR/docker-compose.yml" && -f "$REPO_DIR/.env" ]]; then
  PLATFORM_DIR="$REPO_DIR"
  INSTALLER_LAYOUT=true
else
  PLATFORM_DIR="$REPO_DIR/platform"
  INSTALLER_LAYOUT=false
fi

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

log "Preflight checks"
command -v docker >/dev/null 2>&1 || fail "docker is not installed"
docker compose version >/dev/null 2>&1 || fail "docker compose v2 is not available"
command -v git >/dev/null 2>&1 || fail "git is not installed"
repo_git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || fail "not a git checkout: $REPO_DIR"
[[ -f "$PLATFORM_DIR/.env" ]] || fail "missing $PLATFORM_DIR/.env"

if [[ -z "$DB_USER" ]]; then
  DB_USER="$(env_value POSTGRES_USER "$PLATFORM_DIR/.env")"
  DB_USER="${DB_USER:-labuser}"
fi
if [[ -z "$DB_NAME" ]]; then
  DB_NAME="$(env_value POSTGRES_DB "$PLATFORM_DIR/.env")"
  DB_NAME="${DB_NAME:-labdb}"
fi

if ! repo_git remote get-url "$REMOTE" >/dev/null 2>&1; then
  if [[ "$REMOTE" == "origin" ]] && repo_git remote get-url backup >/dev/null 2>&1; then
    warn "remote 'origin' not found; using the legacy 'backup' remote"
    REMOTE=backup
  else
    fail "git remote '$REMOTE' does not exist"
  fi
fi

if [[ -n "$(repo_git status --porcelain --untracked-files=no)" ]]; then
  fail "the checkout has uncommitted changes; commit or stash them before upgrading"
fi

COMPOSE=()
if [[ -f "$PLATFORM_DIR/docker-compose.yml" ]]; then
  COMPOSE=(docker compose -f "$(docker_path "$PLATFORM_DIR/docker-compose.yml")")
elif [[ -f "$PLATFORM_DIR/docker-compose.prod.yml" ]]; then
  COMPOSE=(docker compose -f "$(docker_path "$PLATFORM_DIR/docker-compose.prod.yml")")
else
  fail "no docker-compose.yml or docker-compose.prod.yml in $PLATFORM_DIR"
fi
if [[ -f "$PLATFORM_DIR/docker-compose.override.yml" ]]; then
  COMPOSE+=(-f "$(docker_path "$PLATFORM_DIR/docker-compose.override.yml")")
fi
# Optional operator layer. Existing deployments use it to pin a named volume
# (for example adopting the Postgres volume that already holds the data)
# without editing tracked compose files. Keep it last so it wins.
if [[ -f "$PLATFORM_DIR/docker-compose.adopt.yml" ]]; then
  COMPOSE+=(-f "$(docker_path "$PLATFORM_DIR/docker-compose.adopt.yml")")
fi
compose() { "${COMPOSE[@]}" "$@"; }
# Git Bash rewrites absolute container paths such as /tmp/x into Windows paths
# before Docker sees them. Disable that conversion for exec/cp arguments.
compose_in() { MSYS_NO_PATHCONV=1 "${COMPOSE[@]}" "$@"; }
COMPOSE_DISPLAY="$(printf '%q ' "${COMPOSE[@]}")"

# Installer deployments build from copies in backend/ and frontend/, so pull
# the updated source from platform/ before recreating the containers. The
# deployed frontend/wiki tree is generated separately and must be preserved.
sync_installed_code() {
  local tree src dst
  log "Syncing platform source into the installed deployment"
  for tree in backend frontend db; do
    src="$REPO_DIR/platform/$tree"
    dst="$PLATFORM_DIR/$tree"
    [[ -d "$src" ]] || continue
    mkdir -p "$dst"
    if command -v rsync >/dev/null 2>&1; then
      if [[ "$tree" == "frontend" ]]; then
        rsync -rlpt --delete --exclude='__pycache__' --exclude='wiki' "$src/" "$dst/"
      else
        rsync -rlpt --delete --exclude='__pycache__' "$src/" "$dst/"
      fi
    elif [[ "$tree" == "frontend" ]]; then
      find "$src" -mindepth 1 -maxdepth 1 ! -name '__pycache__' ! -name 'wiki' \
        -exec cp -r {} "$dst/" \;
    else
      find "$src" -mindepth 1 -maxdepth 1 ! -name '__pycache__' \
        -exec cp -r {} "$dst/" \;
    fi
    if [[ "$EUID" -eq 0 && -n "${SUDO_USER:-}" ]]; then
      chown -R "$SUDO_USER:$SUDO_USER" "$dst" 2>/dev/null || true
    fi
  done
  chmod +x "$PLATFORM_DIR/db/"*.sh 2>/dev/null || true
}

if [[ "$SKIP_USERS" == false && ! -f "$USER_TRANSFER" ]]; then
  fail "scripts/user_transfer.py is missing; copy it to the server or use --skip-users"
fi

log "Repository: $REPO_DIR"
log "Scripts:    $SCRIPT_DIR"
log "Deployment: $PLATFORM_DIR"
log "Layout:     $(if [[ "$INSTALLER_LAYOUT" == true ]]; then echo installed; else echo checkout; fi)"
log "Remote:     $REMOTE/$BRANCH"
log "Database:   $DB_USER@$DB_NAME"

ensure_labs_host_path

if [[ "$SKIP_VERIFY" == false ]]; then
  CURRENT_STEP="preflight verification"
  log "Running read-only preflight verification"
  bash "$SCRIPT_DIR/verify-upgrade.sh" \
    --repo "$REPO_DIR" \
    --remote "$REMOTE" \
    --branch "$BRANCH" \
    --db-user "$DB_USER" \
    --db-name "$DB_NAME" \
    --backup-root "$BACKUP_ROOT"
fi

# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

CURRENT_STEP="backup"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$BACKUP_ROOT/ocr-$TIMESTAMP"
log "Creating backup at $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR" 2>/dev/null || true

cp "$PLATFORM_DIR/.env" "$BACKUP_DIR/.env"
for f in docker-compose.yml docker-compose.prod.yml docker-compose.override.yml docker-compose.adopt.yml; do
  [[ -f "$PLATFORM_DIR/$f" ]] && cp "$PLATFORM_DIR/$f" "$BACKUP_DIR/$f"
done
[[ -d "$PLATFORM_DIR/certs" ]] && cp -R "$PLATFORM_DIR/certs" "$BACKUP_DIR/certs"

log "Starting database and backend for the backup"
compose up -d db backend >/dev/null

log "Dumping the database"
compose_in exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$BACKUP_DIR/database.dump"
[[ -s "$BACKUP_DIR/database.dump" ]] || fail "database dump is empty"

if [[ "$SKIP_USERS" == false ]]; then
  log "Exporting users"
  compose_in cp "$(docker_path "$USER_TRANSFER")" backend:/tmp/user_transfer.py >/dev/null
  compose_in exec -T backend python /tmp/user_transfer.py export -o /tmp/users-export.json
  compose_in cp backend:/tmp/users-export.json "$(docker_path "$BACKUP_DIR/users-export.json")" >/dev/null
  compose_in exec -T backend rm -f /tmp/user_transfer.py /tmp/users-export.json
  chmod 600 "$BACKUP_DIR/users-export.json" 2>/dev/null || true
fi

# The suppression ledger is outside PostgreSQL so a database restore cannot
# overwrite it. Copy it for disaster recovery, but restore procedures must use
# the live file and re-apply it after importing an older dump.
if compose_in exec -T backend test -f "$ERASURE_LEDGER_PATH"; then
  log "Copying erasure suppression ledger"
  compose_in cp "backend:$ERASURE_LEDGER_PATH" "$(docker_path "$BACKUP_DIR/erasure-ledger.jsonl")" >/dev/null
  chmod 600 "$BACKUP_DIR/erasure-ledger.jsonl" 2>/dev/null || true
fi

cat > "$BACKUP_DIR/README.txt" <<EOF
OpenCyberRange backup: $BACKUP_DIR

Files:
  database.dump       PostgreSQL custom-format dump
  users-export.json   Portable user export (password hashes; sensitive)
  erasure-ledger.jsonl Suppression hashes for deleted accounts (if present)
  .env                Platform environment
  docker-compose*     Compose configuration
  certs/              TLS certificates, if present

Full database restore (destructive):
  ${COMPOSE_DISPLAY}stop backend frontend
  cat "$BACKUP_DIR/database.dump" | ${COMPOSE_DISPLAY}exec -T db pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists
  ${COMPOSE_DISPLAY}up -d backend frontend
  # A dump may predate deletion requests. Re-apply the LIVE ledger (not the
  # copy in this backup) so erased accounts cannot come back:
  ${COMPOSE_DISPLAY}cp "$(docker_path "$REPO_DIR/scripts/purge_erased_accounts.py")" backend:/tmp/purge_erased_accounts.py
  ${COMPOSE_DISPLAY}exec -T backend python /tmp/purge_erased_accounts.py --dry-run
  ${COMPOSE_DISPLAY}exec -T backend python /tmp/purge_erased_accounts.py

User merge only:
  ${COMPOSE_DISPLAY}cp "$(docker_path "$BACKUP_DIR/users-export.json")" backend:/tmp/users-export.json
  ${COMPOSE_DISPLAY}exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --ledger "$ERASURE_LEDGER_PATH" --dry-run
  ${COMPOSE_DISPLAY}exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --ledger "$ERASURE_LEDGER_PATH"

The user export contains password hashes and personal data. Delete this backup
directory after the upgrade has been verified and retained elsewhere if needed.
Backups older than ${BACKUP_RETENTION_DAYS} days are removed automatically after a
successful upgrade (set --backup-retention-days 0 to keep them).
EOF
log "Backup complete: $BACKUP_DIR"

# ---------------------------------------------------------------------------
# Pull and deploy
# ---------------------------------------------------------------------------

CURRENT_STEP="git fetch/merge"
OLD_COMMIT="$(repo_git rev-parse HEAD)"
log "Fetching $REMOTE/$BRANCH"
if ! repo_git fetch "$REMOTE" \
    "+refs/heads/$BRANCH:refs/remotes/$REMOTE/$BRANCH"; then
  fail "could not fetch $REMOTE/$BRANCH; try: git -C $REPO_DIR fetch $REMOTE $BRANCH"
fi
log "Fast-forwarding to $REMOTE/$BRANCH"
repo_git merge --ff-only "$REMOTE/$BRANCH"
NEW_COMMIT="$(repo_git rev-parse HEAD)"

if [[ "$INSTALLER_LAYOUT" == true ]]; then
  CURRENT_STEP="platform sync"
  sync_installed_code
  if [[ -f "$REPO_DIR/platform/scripts/init_database.sh" ]]; then
    log "Initializing database schema (idempotent)"
    (cd "$PLATFORM_DIR" && bash "$REPO_DIR/platform/scripts/init_database.sh") \
      || fail "database initialization failed"
  fi
fi

CURRENT_STEP="docker build/recreate"
log "Rebuilding and recreating database, backend, and frontend"
compose up -d --build db backend frontend

if [[ "$INSTALLER_LAYOUT" == true ]] && command -v systemctl >/dev/null 2>&1; then
  if systemctl is-enabled ocr-vpn-firewall.service >/dev/null 2>&1; then
    systemctl restart ocr-vpn-firewall.service >/dev/null 2>&1 \
      && log "Re-applied VPN firewall rules" \
      || warn "could not restart ocr-vpn-firewall.service"
  fi
fi

CURRENT_STEP="backend health"
log "Waiting for the backend health endpoint"
READY=false
for _ in $(seq 1 60); do
  if compose_in exec -T backend curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    READY=true
    break
  fi
  sleep 2
done
[[ "$READY" == true ]] || fail "backend did not become healthy"

if [[ "$SKIP_DISCOVERY" == false ]]; then
  CURRENT_STEP="curriculum/discovery"
  log "Seeding curriculum and discovering labs"
  compose_in exec -T backend python -m app.scripts.seed_curriculum
  compose_in exec -T backend python /app/app/scripts/discover_labs.py
fi

if [[ "$PREBUILD_LABS" == true ]]; then
  CURRENT_STEP="lab image prebuild"
  log "Rebuilding all lab images (cached layers are reused where possible)"
  PREBUILD_SCRIPT="$REPO_DIR/scripts/prebuild-labs.sh"
  [[ -f "$PREBUILD_SCRIPT" ]] || PREBUILD_SCRIPT="$SCRIPT_DIR/prebuild-labs.sh"
  bash "$PREBUILD_SCRIPT" --parallel "$PREBUILD_PARALLEL"
fi

if [[ "$SKIP_RANGEBOX" == false ]]; then
  CURRENT_STEP="rangebox images"
  log "Rebuilding RangeBox images: Kali, Ubuntu, and REMnux"
  docker build --pull -t "$RANGEBOX_IMAGE" "$REPO_DIR/RangeBox"
  docker build --pull -t "$UBUNTUBOX_IMAGE" "$REPO_DIR/UbuntuBox"
  docker build --pull -t "$REMNUX_IMAGE" "$REPO_DIR/RemnuxBox"
fi

if [[ "$SKIP_USERS" == false ]]; then
  CURRENT_STEP="user merge"
  log "Merging users from the backup (existing users are preserved by default)"
  compose_in cp "$(docker_path "$USER_TRANSFER")" backend:/tmp/user_transfer.py >/dev/null
  compose_in cp "$(docker_path "$BACKUP_DIR/users-export.json")" backend:/tmp/users-export.json >/dev/null
  if [[ "$UPDATE_USERS" == true ]]; then
    compose_in exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --update --ledger "$ERASURE_LEDGER_PATH"
  else
    compose_in exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --ledger "$ERASURE_LEDGER_PATH"
  fi
  compose_in exec -T backend rm -f /tmp/user_transfer.py /tmp/users-export.json
fi

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

CURRENT_STEP="verification"
log "Container status"
compose ps

log "Backend health"
compose_in exec -T backend curl -fsS http://localhost:8000/health
printf '\n'

log "User count"
compose_in exec -T db psql -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT count(*) FROM users;"

CURRENT_STEP="post-install checks"
log "Running post-install health checks"
bash "$SCRIPT_DIR/verify-upgrade.sh" --runtime-only \
  --repo "$REPO_DIR" --db-user "$DB_USER" --db-name "$DB_NAME"

CURRENT_STEP="backup retention"
if [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] && [[ "$BACKUP_RETENTION_DAYS" -gt 0 ]]; then
  log "Pruning completed backups older than ${BACKUP_RETENTION_DAYS} days"
  find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'ocr-*' \
    -mtime +"$BACKUP_RETENTION_DAYS" -print -exec rm -rf {} + \
    || warn "backup retention cleanup failed; review $BACKUP_ROOT manually"
fi

LAB_STATUS="rebuilt"
[[ "$PREBUILD_LABS" == true ]] || LAB_STATUS="skipped (--skip-labs)"
RANGEBOX_STATUS="rebuilt"
[[ "$SKIP_RANGEBOX" == false ]] || RANGEBOX_STATUS="skipped (--skip-rangebox)"

cat <<EOF

[✓] Upgrade complete
    Previous commit: $OLD_COMMIT
    Current commit:  $NEW_COMMIT
    Backup:          $BACKUP_DIR
    Backups kept:    ${BACKUP_RETENTION_DAYS} days
    Lab images:      $LAB_STATUS
    RangeBox images: $RANGEBOX_STATUS

Next steps:
  - Log in and verify a migrated account and the exercise catalogue.
  - Verify the frontend over HTTPS.
  - Delete the backup directory after confirming the upgrade, or move it to
    secure storage. It contains password hashes and personal data.
EOF
