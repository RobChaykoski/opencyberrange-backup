# Supported Versions

This file records the platform baseline, the target for the latest-supported-GA
upgrade, and the reason for every exception. It is the human-readable companion
to `versions.yaml`.

Last reviewed: **2026-11-01**.

## Policy

- Target the newest **stable, generally available** release that is still
  supported upstream and compatible with the rest of the stack.
- Do not use alpha, beta, release-candidate, nightly, or `-rolling` tags for
  platform services. `kalilinux/kali-rolling` remains the deliberate RangeBox
  exception.
- Prefer the latest patch/minor in a supported major. Move majors one wave at a
  time.
- Pin exact versions and image digests for platform services.
- Do not upgrade intentionally vulnerable lab software.
- Every exception needs an owner, a reason, and an expiry/review date.

## Platform runtime

| Component | Current | Target | Status | Notes |
|---|---|---|---|---|
| Python | 3.11 | 3.13 | Remaining (runtime wave) | Re-evaluate 3.14 after wheels |
| Node.js | 22 LTS | 24 LTS | Applied in Wave C | Re-evaluate 24 LTS next |
| PostgreSQL | 15 | 17 | Planned major upgrade | Separate deployment, dump/restore |
| Backend base | `python:3.11-slim` | Pin a 3.13 slim digest | Wave 1 | psycopg3/cryptography wheels are available; test the runtime swap |
| Frontend builder | `node:22-alpine` | Pin a digest | Applied in Wave C | Required by Vite 8 |
| Frontend server | `nginx:alpine` | Pin a supported stable digest | Wave 1 | Verify nginx config compatibility |

## Backend dependencies

| Component | Current | Planned wave | Notes |
|---|---|---|---|
| FastAPI | 0.162.0 (Starlette 1.10) | Wave C (done) | |
| Uvicorn | 0.54.0 | Wave C (done) | |
| Pydantic | 2.14.2 | Wave C (done) | |
| python-multipart | 0.0.33 | Wave A (done) | |
| slowapi | 0.1.10 | Wave A (done) | Verified on Starlette 1.x |
| cryptography | 50.0.2 | Wave A (done) | Fernet and JWT tested |
| PyJWT | 2.15.1 | Wave B (done) | Replaced python-jose |
| pwdlib + bcrypt | 0.3.1 + 5.0.0 | Wave B (done) | Argon2id; legacy bcrypt rehashed on login |
| SQLAlchemy | 2.1.6 | Wave C (done) | |
| Alembic | 1.20.1 | Wave C (done) | |
| psycopg (v3) | 3.3.6 | Wave C (done) | SQLAlchemy 2.1 defaults to psycopg3 |
| docker SDK | 7.2.0 | Wave C (done) | |
| aiohttp / requests | 3.14.5 / 2.34.2 | Wave A (done) | |
| APScheduler | 3.10.4 | 4 | Stay on 3.x unless 4.x is justified |
| fpdf2 / matplotlib / qrcode | 2.9.0 / >=3.10 / 8.2 | Wave A/C (done) | Transcript, charts, QR |

## Frontend dependencies

The lockfile is newer than the declared ranges. The locked versions are the
baseline; Wave 5 updates the runtime and Wave 1 updates the toolchain.

| Component | Locked | Planned wave | Notes |
|---|---|---|---|
| Vue | 3.5.44 | Locked | |
| Vue Router | 4.6.4 | 5 | |
| Axios | 1.21.0 | Wave A (done) | |
| Chart.js / vue-chartjs | 4.5.1 / 5.3.3 | 5 | |
| marked | 18.1.2 | Wave A (done) | |
| DOMPurify | 3.4.17 | Wave A (done) | Keep sanitisation tests |
| noVNC | 1.7.0 | Wave C (done) | Required for Vite 8 (Rolldown) |
| sortablejs | 1.15.7 | 5 | |
| Vite | 8.3.5 | Wave C (done) | Rolldown; Node 22+ |
| @vitejs/plugin-vue | 6.0.10 | Wave C (done) | Pairs with Vite 8 |
| ESLint / plugin-vue | 9.39.5 / 9.33.0 | 1 | ESLint 9 flat config |
| globals | 15.15.0 | 1 | |

## Infrastructure, docs, and CI

| Component | Current | Target | Notes |
|---|---|---|---|
| PostgreSQL image | `postgres:15-alpine` | `postgres:17-alpine` digest | Wave 6 |
| MkDocs | 1.6.1 | Newest compatible 1.x | Do not move to 2.0 until Material supports it |
| Material for MkDocs | 9.8.0 | Newest 9.x | |
| pymdown-extensions | 11.0.1 | Newest compatible | Required by Material 9.8 |
| CodeQL action | v4 | Current major | Renovate |
| Trivy action | 0.36.0 | Current | Renovate |
| checkout action | v7 | Current major | Renovate |

## Out of scope

The following remain on their current bases in this programme:

- `platform/labs/**` — including ~148 Ubuntu 22.04 images, Alpine 3.18/3.19,
  PHP 8.1, MySQL 8.0, and Python 3.11 mock services.
- `RangeBox/**`, `UbuntuBox/**`, `RemnuxBox/**`.

Some of those pins are intentionally vulnerable. They need a separate lab
upgrade programme with per-lab solve tests.

## Exceptions and review

| Exception | Reason | Review |
|---|---|---|
| Kali rolling in RangeBox | Rolling is the intended upstream channel | Each RangeBox rebuild |
| Frozen lab service versions | Intentionally vulnerable exercise targets | Separate lab programme |
| MkDocs 1.x | MkDocs 2.0 is incompatible with Material | When Material supports 2.x |
| APScheduler 3.x | 4.x is a major API rewrite | Revisit after platform waves |

See [UPGRADE-TO-LATEST-GA-PLAN.md](UPGRADE-TO-LATEST-GA-PLAN.md) for the full
wave plan, gates, and rollback procedure.
