# Upgrade and Verify a Server

Use the verification script before an upgrade, then run the upgrade script. The
full upgrade backs up the current state, fast-forwards the checkout, rebuilds
the platform, refreshes every lab image, rebuilds all three RangeBox images,
and merges the existing users.

## Already running an older checkout?

If `scripts/verify-upgrade.sh` is not on the server yet, fetch the repository
once into a temporary directory and point the scripts at the live deployment.
`--repo` is the Git checkout that holds the running deployment: installed
servers have `.env` and `docker-compose.yml` at that top level, and development
checkouts have them under `platform/`. Adjust the path if the platform is
installed somewhere else.

For an installed server, the upgrade copies the updated `platform/backend`,
`platform/frontend`, and `platform/db` trees into the deployment before
rebuilding, while preserving the generated `frontend/wiki` tree.

```bash
git clone --depth 1 --branch main \
  https://github.com/RobChaykoski/opencyberrange.git /tmp/ocr-upgrade

sudo bash /tmp/ocr-upgrade/scripts/verify-upgrade.sh \
  --repo "$HOME/opencyberrange" --remote origin --branch main

sudo bash /tmp/ocr-upgrade/scripts/upgrade-from-backup.sh \
  --repo "$HOME/opencyberrange" --remote origin --branch main
```

The existing deployment must be a Git checkout, and it must have a remote that
contains the branch being deployed:

```bash
cd "$HOME/opencyberrange"
git remote -v
git remote add origin https://github.com/RobChaykoski/opencyberrange.git
```

Existing deployments that still use a remote named `backup` can either keep it
and pass `--remote backup`, or point it at the canonical repository:

```bash
git remote set-url backup https://github.com/RobChaykoski/opencyberrange.git
```

The scripts prefer `origin` and fall back to `backup` when `origin` is absent.

For a private repository, configure a deploy key or personal access token on
the server first. The upgrade fetches the remote itself, so you do not need to
copy files to the server by hand.

## 1. Verify first

Run from the repository root on the server:

```bash
sudo bash scripts/verify-upgrade.sh --remote origin --branch main
```

The verification is read-only. It checks:

- Docker, Compose, Git, and the repository state
- `platform/.env` and the detected database target
- The compose configuration and running `db`, `backend`, and `frontend`
- PostgreSQL connectivity and the `users` table
- Backend and frontend health endpoints
- The Git remote and whether the checkout can fast-forward
- Backup path, free disk space, and a schema-only `pg_dump`
- The user export and an import dry-run
- Every lab definition under `platform/labs`
- The `RangeBox`, `UbuntuBox`, and `RemnuxBox` build sources and images

**What you should see:** all checks pass, with warnings for optional HTTPS or a
RangeBox image that has not been built yet. If any check fails, fix it before
upgrading.

## Post-install checks

After an installation or upgrade, run the read-only runtime check:

```bash
bash scripts/post-install-check.sh
```

It checks the containers, database connectivity, schema drift, user count, lab
definitions, RangeBox images, health endpoints, and disk. It exits non-zero if
a required check fails, and it does not check Git state or write to the
database. When running it from a temporary clone, pass `--repo`:

```bash
bash /tmp/ocr-upgrade/scripts/post-install-check.sh \
  --repo "$HOME/opencyberrange"
```

## 2. Upgrade

```bash
sudo bash scripts/upgrade-from-backup.sh --remote origin --branch main
```

The upgrade performs the following in order:

| Step | What happens |
|------|--------------|
| Preflight | Runs `verify-upgrade.sh` unless `--skip-verify` is set |
| Backup | Creates a timestamped directory under `~/opencyberrange-backups/` |
| Database | Exports a full `pg_dump` in custom format |
| Users | Exports every user to `users-export.json` |
| Erasure ledger | Copies the deleted-account suppression ledger, if present |
| Config | Copies `.env`, compose files, and certificates |
| Source | Fetches and fast-forwards to the selected remote branch |
| Platform | Rebuilds and recreates `db`, `backend`, and `frontend` |
| Curriculum | Runs the curriculum seeder and lab discovery |
| Lab images | Rebuilds every lab image with `prebuild-labs.sh` |
| RangeBox | Rebuilds Kali, Ubuntu, and REMnux images |
| Users | Merges the user export; existing accounts are preserved by default and erased accounts are skipped |
| Verify | Checks container status, backend health, and the user count |
| Retention | Prunes completed backups older than 30 days (configurable) |

By default all lab images and all RangeBox images are rebuilt. The first full
run can take a long time and needs significant disk space. The default REMnux
image is about 6 GB compressed and 14 GB on disk.

## Common options

```bash
# Skip the read-only verification only when you have just run it manually
sudo bash scripts/upgrade-from-backup.sh --skip-verify

# Code-only upgrade: no lab image or RangeBox rebuild
sudo bash scripts/upgrade-from-backup.sh --skip-labs --skip-rangebox

# Rebuild lab images four at a time
sudo bash scripts/upgrade-from-backup.sh --prebuild-parallel 4

# Refresh existing users from the backup instead of only adding missing ones
sudo bash scripts/upgrade-from-backup.sh --update-users

# Leave users untouched
sudo bash scripts/upgrade-from-backup.sh --skip-users

# Skip curriculum seeding and lab discovery
sudo bash scripts/upgrade-from-backup.sh --skip-discovery

# Change backup retention (0 keeps every backup)
sudo bash scripts/upgrade-from-backup.sh --backup-retention-days 14
```

## Compose error: empty section between colons

If Docker reports `invalid spec: :/labs:ro: empty section between colons`, the
`LABS_HOST_PATH` value in `platform/.env` is empty. Set it to the absolute path
of the labs directory on the host:

```bash
cd /opt/opencyberrange          # or your checkout path
if [ -d platform/labs ]; then
  LABS_DIR="$(cd platform/labs && pwd)"
else
  LABS_DIR="$(cd labs && pwd)"
fi
sed -i "s|^LABS_HOST_PATH=.*|LABS_HOST_PATH=$LABS_DIR|" platform/.env
grep '^LABS_HOST_PATH=' platform/.env
```

If the line is missing entirely, append it:

```bash
printf '\nLABS_HOST_PATH=%s\n' "$LABS_DIR" >> platform/.env
```

Then rerun the upgrade. The upgrade script now derives this value when it is
empty, and `verify-upgrade.sh` fails with a clear message if it is still
missing.

## Erased accounts and restores

Deleted accounts are recorded in an append-only suppression ledger on the
backend's persistent `/workbook` volume. The upgrade script copies it into the
backup and skips those accounts when merging `users-export.json`.

A database dump can predate a deletion. After any full restore, re-apply the
live ledger so the account cannot come back:

```bash
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  cp scripts/purge_erased_accounts.py backend:/tmp/purge_erased_accounts.py
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  exec -T backend python /tmp/purge_erased_accounts.py --dry-run
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  exec -T backend python /tmp/purge_erased_accounts.py
```

Backups contain password hashes and personal data. Keep them access-controlled
and delete them when the retention period ends. See
[Privacy, Erasure, and Backups](../04_Admin_Guide/27_Privacy_And_Erasure.md) for
the full data map and retention guidance.

Use `--skip-labs` or `--skip-rangebox` only when you know those images are
already current. Lab definitions are still refreshed unless
`--skip-discovery` is also used.

## Backups and rollback

Each run creates:

```text
~/opencyberrange-backups/ocr-YYYYMMDD-HHMMSS/
├── database.dump
├── users-export.json
├── .env
├── docker-compose*.yml
├── certs/
└── README.txt
```

When the script is run with `sudo`, `~/opencyberrange-backups` resolves to
root's home. Pass `--backup-root DIR` if you want the backup elsewhere.

The user export contains password hashes. The directory is created with
restrictive permissions; delete it after the upgrade is verified or move it to
secure storage.

The upgrade script prints the restore instructions and writes them to the
backup's `README.txt`. A full database restore is destructive; stop the
backend and frontend before restoring.

If the upgrade fails, the script stops at the failed step and prints the backup
path. The source checkout is already fast-forwarded, so fix the reported problem
and rerun the script; the backup step is safe to repeat.

## What is not migrated

- MFA/TOTP enrollment and recovery codes
- Trusted devices and active sessions
- WireGuard VPN peers and configuration
- Course enrollments, completions, achievements, and lab history

See [Migrating Users](../04_Admin_Guide/26_Migrating_Users.md) for the user-only
workflow and its limitations.
