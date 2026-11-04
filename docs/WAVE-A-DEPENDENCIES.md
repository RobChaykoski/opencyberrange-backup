# Wave A — dependency security patches

Applied: 2026-11-02
Scope: platform only (`platform/backend`, `platform/frontend`). Lab and
RangeBox images untouched, per the version policy.

## Applied

| Package | From | To | Reason |
|---|---|---|---|
| aiohttp | 3.9.3 | 3.14.5 | 80 advisories (DoS, request smuggling, header parsing) |
| cryptography | 41.0.7 | 50.0.2 | 14 advisories (TLS/X.509/PKCS) |
| python-multipart | 0.0.6 | 0.0.33 | 16 advisories (ReDoS, boundary parsing) |
| python-jose | 3.3.0 | 3.5.0 | 6 advisories; keeps the cryptography upgrade compatible |
| requests | 2.31.0 | 2.34.2 | 6 advisories (proxy/header handling) |
| fpdf2 | 2.7.9 | 2.9.0 | 2 advisories |
| fastapi | 0.109.0 | 0.109.1 | single patch advisory |
| psycopg2-binary | 2.9.9 | 2.9.13 | patch set |
| pyyaml | 6.0.1 | 6.0.3 | patch set |
| pyotp | 2.9.0 | 2.10.0 | patch set |
| email-validator | 2.1.0 | 2.3.0 | patch set |
| slowapi | 0.1.9 | 0.1.10 | patch set |
| axios | 1.13.6 | 1.21.0 | security fixes in the HTTP client |
| dompurify | 3.3.3 | 3.4.17 | sanitizer fixes (XSS) |
| marked | 17.0.5 | 18.1.2 | markdown parser fixes |
| postcss / source-map-js (transitive) | — | patched | `npm audit fix` |

## Verification

- Backend: **61 tests passed** on PostgreSQL 17.
- Frontend: `npm run lint` 0 errors; `npm run build` passed.
- Backend image builds from a clean context with the new pins.
- `npm audit --omit=dev`: **0 vulnerabilities** (was 9, 8 high).

## Advisory count after Wave A

| Package | Remaining | Fix path |
|---|---|---|
| starlette 0.35.1 | 14 | Wave C: FastAPI → 0.162 with Starlette 1.x |
| python-jose 3.5.0 | 1 (no fix listed) | Wave B: replace with `pyjwt[crypto]` |
| ecdsa 0.19.2 | 2 (no fix listed) | Wave B: removed with python-jose |

Before: 9 packages, 141 advisories. After: 3 packages, 17 advisories, all
either blocked on the framework wave or resolved by the auth migration.

## Follow-ups (not in this wave)

- Wave B: PyJWT + `pwdlib[argon2]`, drop `passlib` and the bcrypt 4.0.1 pin.
- Wave C: FastAPI/Starlette 1.x, SQLAlchemy 2.1, Docker SDK 7, qrcode 8,
  Node 22/24 with Vite 8.
- CI: flip `dependency-audit` to blocking once Starlette is cleared.

## Rollback

Revert this commit; the pins are the only change and no schema or API surface
moved. `platform/frontend/package-lock.json` must be reverted with it.
