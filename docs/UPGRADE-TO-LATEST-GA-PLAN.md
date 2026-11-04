# Plan: Build a New Repo on Latest Supported GA Components

Status: planning document. Nothing in this document changes runtime behaviour.

Wave 0 scaffold is present: `versions.yaml`, `docs/SUPPORTED-VERSIONS.md`,
`docs/WAVE-0-BASELINE.md`, `scripts/report-versions.py`, CI workflows, and
Renovate configuration.

## 1. What "latest supported GA" means

Do not equate this with "newest version of everything". The target is the newest
**stable, generally available** release that is:

1. still supported upstream (not EOL);
2. compatible with every other selected component;
3. covered by the project's tests and the lab validation suite.

Rules:

- No alpha, beta, release-candidate, nightly, or `-rolling` tags for platform
  services. `kalilinux/kali-rolling` remains the deliberate exception for
  RangeBox.
- Prefer the latest patch/minor in a supported major. Move majors only in their
  own PR with a compatibility gate.
- Pin exact versions and image digests for platform services.
- Do not upgrade intentionally vulnerable lab software. Those pins are the
  exercise.
- Record every selected version, its EOL date, and the reason for any exception
  in `docs/SUPPORTED-VERSIONS.md`.

## 2. Current baseline (inventory)

### Platform backend

| Component | Current | Notes |
|---|---|---|
| Python | `python:3.11-slim` | 3.11 is in security-only maintenance; 3.13/3.14 are current |
| FastAPI | 0.109.0 | Jan 2024 line |
| Uvicorn | 0.27.0 | |
| SQLAlchemy | 2.0.25 | |
| Alembic | 1.13.1 | |
| Pydantic | 2.5.3 | |
| psycopg2-binary | 2.9.9 | Consider psycopg 3 separately |
| python-jose | 3.3.0 | Old; assess PyJWT or a maintained fork |
| passlib + bcrypt | 1.7.4 + 4.0.1 | passlib is unmaintained; bcrypt 4.1+ is a known breakage |
| cryptography | 41.0.7 | |
| docker SDK | 6.1.3 | Major 7.x available |
| aiohttp / requests | 3.9.3 / 2.31.0 | |
| APScheduler | 3.10.4 | 4.x is a rewrite; likely stay on 3.x |
| fpdf2 / matplotlib / qrcode | 2.7.9 / >=3.10 / 7.4.2 | |
| slowapi | 0.1.9 | Check Starlette compatibility |
| python-multipart | 0.0.6 | Security-relevant; upgrade early |

### Platform frontend

Declared ranges are older than the lockfile. The lockfile currently resolves:

| Component | Locked | Notes |
|---|---|---|
| Vue | 3.5.30 | |
| Vue Router | 4.6.4 | |
| Axios | 1.13.6 | |
| Chart.js / vue-chartjs | 4.5.1 / 5.3.3 | |
| marked | 17.0.5 | |
| DOMPurify | 3.3.3 | |
| noVNC | 1.6.0 | |
| sortablejs | 1.15.7 | |
| Vite | 5.4.21 | Vite 6/7 need newer Node and plugin majors |
| @vitejs/plugin-vue | 4.6.2 | |
| ESLint / eslint-plugin-vue | 9.39.5 / 9.33.0 | ESLint 9 flat config |
| Node build image | `node:18-alpine` | Node 18 is EOL; move to 22 or 24 LTS |
| Nginx | `nginx:alpine` | Floating tag; pin version and digest |

### Platform infrastructure

| Component | Current | Notes |
|---|---|---|
| PostgreSQL | `postgres:15-alpine` | 15 is supported but old; 17/18 need a major upgrade runbook |
| Backend base | `python:3.11-slim` | Debian slim, unpinned patch |
| Frontend base | `node:18-alpine` → `nginx:alpine` | Node EOL; Nginx floating |
| Docker CLI | installed from Docker apt repo in the backend image | Pin or track host compatibility |
| Docs | MkDocs 1.6.1 / Material 9.8.0 / pymdown 11.0.1 | MkDocs 2.0 is currently incompatible with Material |
| CI | `actions/checkout@v7`, CodeQL v4, Trivy 0.36.0 | No build/test workflow exists yet |

### Lab images (separate upgrade tier)

Counts from the current tree:

| Base | Count | Policy |
|---|---|---|
| `ubuntu:22.04` | ~148 | Upgrade to 24.04 only after per-lab validation |
| `alpine:3.19` | ~20 | Upgrade to a supported Alpine line |
| `ubuntu:24.04` | 1 | Already current |
| `python:3.11-slim` | ~6 | Upgrade for mock services, then re-test |
| `mysql:8.0` | ~7 | Intentionally vulnerable or exercise-specific; freeze unless validated |
| `php:8.1-apache` | ~3 | EOL; deliberately vulnerable in some labs; freeze |
| `alpine:3.18` | 2 | EOL; upgrade if not intentionally vulnerable |
| `kalilinux/kali-rolling` | ~2 | Rolling by design |
| `remnux/remnux-distro:noble` | 1 | Track upstream |

The lab tier is the largest and riskiest part. It should not be bundled into the
platform upgrade.

## 3. Repo strategy

Status: implemented. The staging repository was created as
`RobChaykoski/opencyberrange-next` and later renamed to
`RobChaykoski/opencyberrange`; see `CUTOVER-TO-CANONICAL-REPO.md`.

A separate staging repository was used instead of a branch on the production
repo.

- Name: `opencyberrange` (canonical; formerly `opencyberrange-next`).
- Started from `backup/main` at the current commit, preserving history.
- Preserve `LICENSE`, `NOTICE`, `LICENSING.md`, `BUILD_NOTICE.md`, and
  `THIRD_PARTY_NOTICES.md`; this project is PolyForm Noncommercial.
- Keep the pre-cutover `backup` remote as `current` so fixes can be
  cherry-picked.
- Protect `main`; require PR + CI.
- Use short-lived branches per wave:
  - `upgrade/00-baseline`
  - `upgrade/01-ci-tooling`
  - `upgrade/02-backend-web`
  - `upgrade/03-backend-security-data`
  - `upgrade/04-frontend-toolchain`
  - `upgrade/05-frontend-runtime`
  - `upgrade/06-infra-postgres`
  - `upgrade/07-docs`
  - `upgrade/08-labs-infrastructure`
  - `upgrade/09-labs-frozen-review`

Bootstrap (historical record):

```bash
git clone https://github.com/RobChaykoski/opencyberrange-backup.git opencyberrange-next
cd opencyberrange-next
git remote rename origin current
git remote add origin <new-repo-url>
git push -u origin main
```

If the new repo should not share history, use an orphan branch, but keep the
licence and provenance files.

## 4. Tooling to add before upgrading

### Version inventory and policy

- `scripts/report-versions.py` (new): reads `requirements*.txt`,
  `package-lock.json`, all Dockerfiles, compose files, and workflows; prints a
  Markdown/JSON matrix with current version, target version, and EOL source.
- `docs/SUPPORTED-VERSIONS.md`: the human-readable support matrix.
- `versions.lock` or `versions.yaml`: machine-readable pins for CI and
  Renovate.
- Use `https://endoflife.date/api/<product>.json` as the EOL source of truth.

### Dependency automation

- Renovate (preferred over Dependabot for grouped updates):
  - group backend web stack, data stack, security stack, frontend toolchain,
    frontend runtime, infra images, GitHub Actions;
  - `rangeStrategy: pin`;
  - `docker:pinDigests`;
  - major updates require a manual label/approval;
  - schedule weekly, separate lockfile-maintenance PR.
- Python: evaluate `uv` (fast, lockfile) or `pip-compile`. Keep the Dockerfile
  install path reproducible either way.
- Frontend: `npm ci` with the committed lockfile; no floating `npm install` in
  CI.
- Images: build by digest; publish `:next` and immutable `:sha-<short>` tags.
- SBOM: Syft; vulnerability scans: Trivy (upgrade the action), `pip-audit`,
  `npm audit --omit=dev`.
- Licences: `pip-licenses` and `license-checker`; regenerate
  `THIRD_PARTY_NOTICES.md` after each wave.

### CI gates

Add GitHub Actions workflows (currently only CodeQL and Trivy exist):

1. Backend: Python 3.12/3.13/3.14 matrix, `ruff`, `pytest`, `pip-audit`.
2. Frontend: Node 22/24 matrix, `npm ci`, `npm run lint`, `npm run build`,
   `npm audit --omit=dev`.
3. Compose: `docker compose config`, backend/frontend image builds.
4. Database: pytest against Postgres 15/17/18; backup/restore smoke test.
5. Labs: `validate-lab.py` for changed labs; `prebuild-labs.sh` for affected
   images; a representative solve/flag test per track.
6. Security: CodeQL, Trivy, SBOM artifact.
7. Release: signed/tagged images, changelog, upgrade notes.

GitHub-hosted runners are fine for backend/frontend. Lab image builds are heavy;
use a self-hosted runner on the lab host, or build only changed labs in PRs.

## 5. Upgrade waves and gates

### Wave 0 — baseline and CI (no version changes)

- Snapshot current versions into `docs/SUPPORTED-VERSIONS.md`.
- Add `report-versions.py`, CI workflows, Renovate config, SBOM.
- Confirm existing gates: 47 backend tests, frontend build, lint 0 errors,
  compose config, a representative lab.

### Wave 1 — runtime and toolchain images

- Node 18 → start with Node 22 LTS; re-evaluate Node 24 LTS after Wave 0
  compatibility results. Node 18 must not remain.
- Python 3.11 → start with Python 3.13; re-evaluate 3.14 after Wave 0/2 wheel
  and dependency checks. Do not assume 3.14 is safe for every library.
- Pin Nginx to a supported stable line and digest.
- Upgrade `@vitejs/plugin-vue`, Vite, ESLint/plugin-vue, globals together.
- Gate: build/test only; no application dependency changes yet.

### Wave 2 — backend web stack

- FastAPI, Starlette, Uvicorn, Pydantic, pydantic-settings, email-validator,
  python-multipart, slowapi.
- Gate: full backend tests, OpenAPI shape check, login/export/erasure/MFA
  endpoints, rate limiting.

### Wave 3 — backend security and data stack

- cryptography, python-jose/PyJWT decision, passlib/bcrypt decision,
  SQLAlchemy, Alembic, psycopg2/psycopg3 decision.
- Gate: auth, JWT revocation, Fernet encryption, TOTP, password hashing,
  migrations, backup/restore.
- Do not combine the bcrypt/passlib change with anything else. It is the
  highest-risk compatibility item in the backend.

### Wave 4 — backend integrations and reporting

- docker SDK, aiohttp, requests, APScheduler, pywinrm, fpdf2, matplotlib,
  qrcode/Pillow.
- Gate: lab lifecycle, VPN peer API, transcript PDF, certificate QR, MFA QR.

### Wave 5 — frontend runtime

- Vue, Vue Router, Axios, Chart.js/vue-chartjs, marked, DOMPurify, noVNC,
  sortablejs.
- Gate: build, lint, browser smoke tests (login, dashboard, catalogue, lab
  launch, profile privacy panel, admin delete guard, certificate print).

### Wave 6 - PostgreSQL major

- 15 → 17 (decided) in its own deployment.
- Audit extensions, `ensure-db-password.sh`, healthcheck, Alembic.
- Runbook: backup, dump/restore or `pg_upgrade`, verification, rollback.
- Gate: restore the production-sized backup into the new major, run the full
  suite, verify erasure ledger purge and user transfer.

### Wave 7 — docs toolchain

- MkDocs/Material/pymdown.
- MkDocs 2.0 is currently incompatible with Material; stay on the newest
  compatible MkDocs 1.x + Material 9.x until Material supports 2.x.
- Gate: build the manuals and workbooks, check internal links and nav.

### Out of scope: lab and RangeBox images

The decision for this programme is **platform only**. Do not upgrade lab base
images or RangeBox/UbuntuBox/REMnuxBox images here. That includes the ~148
Ubuntu 22.04 lab images, Alpine 3.18/3.19 attacker images, PHP 8.1, MySQL 8.0,
Kali rolling, and REMnux. Some of those pins are intentionally vulnerable and
are part of the exercise.

Keep a separate follow-up programme for lab images with its own catalog:
`upgrade_policy: platform | infrastructure | frozen`. Do not block the platform
release on that work.

## 6. Deployment and rollback

- Build `:next` images and deploy to a staging host first.
- Tag images immutably: `:sha-<short>` plus a moving `:next`.
- Keep the previous image digest and database backup for rollback.
- For PostgreSQL, rollback means restoring the old volume/dump, not only
  retagging the image.
- Verify on staging:
  - login and MFA;
  - dashboard, catalogue, course, admin;
  - Profile privacy export and deletion-blocked path;
  - one lab per track, including VPN/noVNC/RangeBox;
  - backup, restore, and `purge_erased_accounts.py`;
  - certificate and transcript PDFs.
- Promote to production only after a soak period and a clean rollback drill.

## 7. Risks and landmines

| Risk | Mitigation |
|---|---|
| passlib + bcrypt 4.1+ breakage | Isolate in its own PR; prefer direct bcrypt or a maintained replacement; test existing hashes |
| python-jose unmaintained / CVEs | Evaluate PyJWT (already a transitive dependency) or a maintained fork |
| Pydantic/FastAPI/Starlette compatibility | Upgrade as a group; run OpenAPI and validation tests |
| SQLAlchemy/Alembic changes | Run migrations against a production-sized restore |
| PostgreSQL major upgrade | Separate deployment; dump/restore; extension audit |
| Node 18 EOL | Move to 22/24; regenerate lockfile; check Vite plugin majors |
| Vite 6/7 Node requirement | Pair with the Node upgrade; do not upgrade Vite first |
| MkDocs 2 / Material incompatibility | Stay on MkDocs 1.x until Material supports 2.x |
| Lab base upgrades break exercises | Freeze intentionally vulnerable images; per-lab solve tests |
| 148 Ubuntu 22.04 lab images | Batch by track; do not include in platform release |
| Docker CLI API vs host | Pin/test against the host Docker Engine |
| Licence/provenance loss in new repo | Preserve LICENSE/NOTICE/THIRD_PARTY_NOTICES; regenerate notices |

## 8. Effort estimate

| Area | Rough effort |
|---|---|
| Baseline, CI, Renovate, SBOM | 2–4 days |
| Backend dependency waves | 3–5 days |
| Frontend toolchain/runtime | 2–4 days |
| PostgreSQL major + restore drill | 2–3 days plus downtime |
| Docs toolchain | 1–2 days |
| Lab and RangeBox images | Out of scope; separate programme |

## 9. Decisions (locked)

| Decision | Choice |
|---|---|
| Repo | `RobChaykoski/opencyberrange` (formerly `opencyberrange-next`), cloned from `backup/main` |
| Runtime | Start Python 3.13 + Node 22 LTS; let Wave 0/2 compatibility testing decide whether to move to 3.14/Node 24 |
| PostgreSQL | 17, in its own deployment with a dump/restore runbook |
| Lab/RangeBox images | Out of scope for this programme; platform only |
| Release cadence | One wave per PR (recommended; do not use one giant branch) |
| CI runner | GitHub-hosted for platform CI; lab-image runners are out of scope |

## 10. First actions

1. Create `RobChaykoski/opencyberrange` (originally named
   `opencyberrange-next`) from `backup/main`; preserve `LICENSE`, `NOTICE`,
   `LICENSING.md`, `BUILD_NOTICE.md`, and `THIRD_PARTY_NOTICES.md`.
2. Protect `main`; require PR + CI.
3. Add `docs/SUPPORTED-VERSIONS.md`, `scripts/report-versions.py`, CI, and
   Renovate.
4. Run Wave 0 and record the baseline passing state: 47 backend tests, frontend
   build/lint, compose config, one representative lab.
5. Start Wave 1 (Python 3.13 + Node 22 images) without changing application
   packages.
6. Proceed one wave at a time. Do not mix the PostgreSQL 17 major upgrade with
   dependency waves, and do not include lab/RangeBox images.
