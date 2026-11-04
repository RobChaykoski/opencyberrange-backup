# Docker Compose Deployment Manual

This is the direct Docker Compose deployment path for a single Linux server. It
does not use the installer script, so every step is visible and repeatable.

Use this manual when you want to:

- deploy from the canonical repository with `docker compose`;
- control the `.env` file yourself;
- run the platform behind a self-signed certificate or your own TLS
  termination;
- understand exactly which containers, volumes, and ports are involved.

For the guided installer, see [Local Deployment](02_Local_Deployment.md) or
[Cloud Deployment](03_Cloud_Deployment.md). The result is the same platform.

## What gets deployed

| Service | Container | Port | Purpose |
|---|---|---|---|
| `db` | `ocr-db` | internal `5432` | PostgreSQL database |
| `redis` | `ocr-redis` | internal `6379` | Shared rate-limit counters |
| `backend` | `ocr-backend` | `127.0.0.1:8000` | FastAPI API and lab orchestration |
| `frontend` | `ocr-frontend` | `80`, `443` | Vue app, API proxy, HTTPS |

Persistent volumes:

- `postgres_data` — database files
- `workbook_data` — workbook and erasure-ledger state

The repository's `platform/labs` directory is mounted read-only into the
backend as `/labs`.

## 1. Prerequisites

- Ubuntu 22.04 LTS or later, or a comparable Linux server
- Docker Engine 24+ with the Compose v2 plugin
- Git
- 4+ CPU cores, 32 GB RAM minimum, 500 GB disk for a production classroom
- Ports `80/tcp` and `443/tcp` open
- Port `51820/udp` open only if students will use the built-in WireGuard VPN
- A DNS name or static IP students can reach

Check the host:

```bash
docker --version
docker compose version
git --version
```

If Docker is missing, install it from Docker's official repository. Do not use
the snap package on a server that also needs host networking or WireGuard.

## 2. Clone the canonical repository

```bash
git clone https://github.com/RobChaykoski/opencyberrange.git
cd opencyberrange
```

The deployment files live in `platform/`.

## 3. Create the environment file

```bash
cp platform/.env.example platform/.env
chmod 600 platform/.env
```

Generate the secrets:

```bash
# JWT_SECRET, SETUP_TOKEN, WG_API_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"

# WG_ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Edit `platform/.env` and fill in every value. The important ones:

| Variable | What to set |
|---|---|
| `JWT_SECRET` | A fresh 64-character hex string |
| `SETUP_TOKEN` | A fresh one-time token; remove it after setup |
| `POSTGRES_PASSWORD` | A strong password |
| `DATABASE_URL` | Same password, database name, and user as the `POSTGRES_*` values |
| `SERVER_PUBLIC_HOST` | The hostname or IP students type in the browser |
| `CORS_ORIGINS` | `https://<SERVER_PUBLIC_HOST>` (comma-separate extra origins) |
| `LABS_HOST_PATH` | Absolute path to `platform/labs` on this host |
| `WG_SERVER_ENDPOINT` | `<public-ip-or-domain>:51820` for VPN deployments |
| `WG_SERVER_PUBLIC_KEY` | The WireGuard server public key |
| `WG_API_KEY` | A fresh 64-character hex string |
| `WG_ENCRYPTION_KEY` | The Fernet key generated above |
| `DEPLOYMENT_MODE` | `local` for a LAN install, `internet` for public access |
| `RATELIMIT_STORAGE_URI` | `redis://redis:6379/0` (default). Use `memory://` only for single-worker development |

`DATABASE_URL` must match `POSTGRES_USER`, `POSTGRES_PASSWORD`, and
`POSTGRES_DB`. If the password contains URL-reserved characters, percent-encode
it in `DATABASE_URL` or use a URL-safe password.

Set `LABS_HOST_PATH` to an absolute path, for example:

```bash
LABS_HOST_PATH=/opt/opencyberrange/platform/labs
```

An empty `LABS_HOST_PATH` makes Docker mount `:/labs:ro` and the backend cannot
discover labs.

## 4. Generate a certificate (HTTPS)

For a LAN deployment, generate a self-signed certificate for the address
students use:

```bash
sudo bash scripts/generate-self-signed-cert.sh 192.168.1.50
```

Replace the address with the server IP or DNS name. The script writes:

```text
platform/certs/selfsigned.crt
platform/certs/selfsigned.key
```

The frontend entrypoint detects both files at startup and serves HTTPS on 443.
Without them it serves HTTP on 80 only.

For a public domain, you can either:

- place a real certificate at the same two paths, or
- terminate TLS at a reverse proxy and run the frontend on HTTP.

The certificate's SAN must include the exact hostname or IP students use. A
mismatch is a hard browser error, not just a warning.

## 5. Start the platform

From the repository root:

```bash
cd platform
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

Wait for the health checks:

```bash
docker compose --env-file .env -f docker-compose.prod.yml ps
```

Expected:

```text
ocr-db        healthy
ocr-redis     healthy
ocr-backend   healthy
ocr-frontend  healthy
```

Check the API directly:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"healthy","database":"up"}
```

If you generated or replaced certificates after the frontend started, recreate
it:

```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --force-recreate frontend
```

## 6. Complete the first-run setup

Open the address students will use:

```text
https://<SERVER_PUBLIC_HOST>/
```

Accept the self-signed certificate warning on a LAN install. The Setup wizard
creates the first administrator. If `SETUP_TOKEN` is set, enter the same value
from `platform/.env`.

After setup:

1. Sign in as the administrator.
2. Open **Admin Panel → System Health** and confirm the checks are green.
3. Open **Admin Panel → Exercises** and choose **Scan for Exercises**.
4. Remove `SETUP_TOKEN` from `platform/.env` and restart the backend:

```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d backend
```

## 7. Seed curriculum and discover labs

The admin scan is the normal path. To do it from the command line:

```bash
cd platform
docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
  python /app/app/scripts/seed_curriculum.py
docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
  python /app/app/scripts/discover_labs.py
```

`discover_labs.py` reads the `/labs` mount and registers every `lab.yaml` it
finds. Re-run it after adding or changing a lab.

## 8. Self-signed certificate warning

A self-signed certificate warning is expected on a LAN deployment. Students
should accept it once. Do not disable TLS verification globally on student
machines.

For a public deployment, use a certificate from a trusted authority or put the
platform behind a reverse proxy that has one.

## 9. Common operations

All commands below run from `platform/`.

### Logs

```bash
docker compose --env-file .env -f docker-compose.prod.yml logs -f backend
docker compose --env-file .env -f docker-compose.prod.yml logs -f frontend
docker compose --env-file .env -f docker-compose.prod.yml logs -f db
```

### Restart one service

```bash
docker compose --env-file .env -f docker-compose.prod.yml restart backend
docker compose --env-file .env -f docker-compose.prod.yml restart frontend
```

### Stop without deleting data

```bash
docker compose --env-file .env -f docker-compose.prod.yml down
```

This keeps the `postgres_data` and `workbook_data` volumes.

### Delete the deployment and its data

```bash
docker compose --env-file .env -f docker-compose.prod.yml down -v
```

**This deletes the database and workbook volume.** Back up first.

### Update the platform

```bash
cd ~/opencyberrange
git pull --ff-only
cd platform
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

Take a database backup before every update. Re-run lab discovery if the update
adds or changes labs.

## 10. Backup and restore

Create a timestamped backup directory:

```bash
cd platform
source .env
BACKUP_DIR="$HOME/opencyberrange-backups/ocr-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
```

Back up the database, configuration, certificates, and erasure ledger:

```bash
docker compose --env-file .env -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$BACKUP_DIR/database.dump"

cp .env "$BACKUP_DIR/.env"
cp docker-compose.prod.yml "$BACKUP_DIR/"
cp -R certs "$BACKUP_DIR/certs" 2>/dev/null || true

docker compose --env-file .env -f docker-compose.prod.yml cp \
  backend:/workbook/erasure-ledger.jsonl "$BACKUP_DIR/erasure-ledger.jsonl" 2>/dev/null || true
```

The `.env` and database dump contain secrets and password hashes. Keep the
backup directory private and delete it when it is no longer needed.

### Restore the database

Stop the application containers first:

```bash
docker compose --env-file .env -f docker-compose.prod.yml stop backend frontend
```

Then restore:

```bash
docker compose --env-file .env -f docker-compose.prod.yml exec -T db \
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < "$BACKUP_DIR/database.dump"
```

Restore the erasure ledger and restart:

```bash
docker compose --env-file .env -f docker-compose.prod.yml cp \
  "$BACKUP_DIR/erasure-ledger.jsonl" backend:/workbook/erasure-ledger.jsonl
docker compose --env-file .env -f docker-compose.prod.yml up -d
```

After a restore, re-apply the live erasure ledger so deleted accounts cannot be
resurrected from an older dump. See
[Privacy, Erasure, and Backups](../04_Admin_Guide/27_Privacy_And_Erasure.md).

## 11. Troubleshooting

| Symptom | Check | Fix |
|---|---|---|
| `LABS_HOST_PATH` empty or mount error | `grep LABS_HOST_PATH platform/.env` | Set the absolute path to `platform/labs` |
| Backend unhealthy | `docker compose ... logs backend` | Confirm `DATABASE_URL` matches the `POSTGRES_*` values |
| Frontend serves HTTP only | `ls platform/certs` | Add `selfsigned.crt` and `selfsigned.key`, recreate frontend |
| Browser certificate error | Certificate SAN | Regenerate with the exact hostname/IP students use |
| Port 80/443 already in use | `sudo ss -ltnp` | Stop the other web server or change the frontend ports |
| Cannot talk to Docker | `docker info` | Start Docker and add your user to the `docker` group |
| Setup token rejected | `grep SETUP_TOKEN platform/.env` | Use the same value, or blank it on an isolated network |
| Database password changed after first start | Reused `postgres_data` volume | See `platform/db/ensure-db-password.sh`; the container reconciles it |
| Labs missing after update | `Admin Panel → Exercises → Scan` | Run `discover_labs.py` |
| Rate limits reset or behave differently per worker | `docker compose ... ps redis` | Start the bundled Redis service and keep `RATELIMIT_STORAGE_URI=redis://redis:6379/0` |

## 12. Security checklist

- Keep `platform/.env` at mode `600` and never commit it.
- Use strong, unique values for every secret.
- Remove `SETUP_TOKEN` after the first administrator is created.
- Expose only `80/tcp` and `443/tcp` publicly. The backend binds to
  `127.0.0.1:8000`; the database is internal-only.
- Open `51820/udp` only if students use the VPN.
- Back up the database, `.env`, certificates, and erasure ledger regularly.
- Use a trusted certificate for public deployments.
- Treat backups as sensitive: they contain password hashes and personal data.
- Keep Docker and the host operating system patched.

## 13. Command quick reference

```bash
# Start or update
cd platform
docker compose --env-file .env -f docker-compose.prod.yml up -d --build

# Status
docker compose --env-file .env -f docker-compose.prod.yml ps

# Logs
docker compose --env-file .env -f docker-compose.prod.yml logs -f backend

# Restart one service
docker compose --env-file .env -f docker-compose.prod.yml restart backend

# Stop, keep data
docker compose --env-file .env -f docker-compose.prod.yml down

# Stop and delete data
docker compose --env-file .env -f docker-compose.prod.yml down -v

# Seed and discover
docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
  python /app/app/scripts/seed_curriculum.py
docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
  python /app/app/scripts/discover_labs.py
```

## Build workbooks and lab images

The workbook wiki and lab images are build artifacts. Build them before
starting or updating the frontend:

```bash
# From the repository root
scripts/build-wiki.sh          # build the wiki_data volume (tracks + manual)
scripts/prebuild-labs.sh --changed
scripts/verify-lab-builds.sh
```

`scripts/build-assets.sh all` runs all three. The wiki builder is a pinned
container image, so the host does not need MkDocs installed. The frontend
mounts `wiki_data` read-only at `/usr/share/nginx/wiki`; the frontend image no
longer contains the wiki.

Set `LAB_ALLOW_ON_DEMAND_BUILD=false` in `.env` after the initial prebuild.
Spawn then fails with a clear message if an image is missing, instead of
starting a slow build while a student waits.

The lab manifest at `scripts/.lab-build-manifest.json` is generated. Keep it
on the host between deploys; `--changed` uses it to skip labs whose source hash
and stable `ocr-lab/<slug>-<service>:latest` tags are unchanged.
