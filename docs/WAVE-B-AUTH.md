# Wave B — auth and crypto consolidation

Applied: 2026-11-02
Scope: platform backend. Lab images untouched.

## What changed

| Area | Before | After |
|---|---|---|
| JWT | `python-jose[cryptography]` 3.5.0 | `pyjwt[crypto]` 2.15.1 |
| Password hashing | `passlib[bcrypt]` 1.7.4 + `bcrypt` 4.0.1 | `pwdlib[argon2]` 0.3.1, Argon2id default, `bcrypt` 5.0.0 as a legacy verifier |
| Hash upgrade | none | successful login rewrites a legacy bcrypt hash to Argon2id |
| Token decode | `jose.JWTError` | `jwt.PyJWTError` (aliased as `JWTError`) |

Code touched: `app/auth.py` (hashing, verification, upgrade-on-login),
`app/main.py` and `app/routers/rangebox.py` (token decode imports),
`app/scripts/seed_demo_class.py` (hash import), tests.

## Why

- `python-jose` carried advisories with no fix and pulled `ecdsa`, which also
  has no fix. PyJWT is maintained, smaller, and is what FastAPI documents.
- `passlib` has been unmaintained since 2020 and forced the `bcrypt==4.0.1`
  pin. `pwdlib` is the FastAPI-recommended replacement and supports Argon2id.
- Argon2id is the current OWASP recommendation for new password storage.

## Compatibility

- Existing bcrypt hashes verify through `BcryptHasher` and are transparently
  rehashed to Argon2id on the next successful login.
- `user_transfer` exports/imports the hash string unchanged, so portable
  accounts keep working; the export test now accepts both `$argon2` and `$2`.
- JWT payloads, `jti` revocation, impersonation checks and the refresh path
  are unchanged; only the library changed.

## Verification

- Backend: **62 tests pass** (61 + a new legacy-bcrypt-upgrade case).
- `pip-audit -r requirements.txt`: **1 package, 14 advisories** — Starlette
  only, cleared by Wave C (FastAPI 0.162 / Starlette 1.x).
- Backend image builds cleanly.

## Rollback

Revert the commit. Existing Argon2 hashes would then be unreadable by passlib,
so rollback also requires restoring the pre-wave database dump
(`upgrade-from-backup.sh` takes one automatically).
