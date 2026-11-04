# Wave C — framework and runtime majors

Applied: 2026-11-02
Scope: platform backend and frontend. Lab images untouched.

## Applied

| Area | From | To |
|---|---|---|
| FastAPI | 0.109.1 | **0.162.0** |
| Starlette (transitive) | 0.35.1 | **1.x** |
| Pydantic / settings | 2.5.3 / 2.1.0 | **2.14.2 / 2.16.2** |
| Uvicorn | 0.27.0 | **0.54.0** |
| SQLAlchemy | 2.0.25 | **2.1.6** |
| Alembic | 1.13.1 | **1.20.1** |
| PostgreSQL driver | psycopg2-binary 2.9.13 | **psycopg 3.3.6** (binary) |
| Docker SDK | 6.1.3 | **7.2.0** |
| qrcode | 7.4.2 | **8.2** |
| Node (builder + CI) | 18 | **22** |
| Vite | 5.4.21 | **8.3.5** (Rolldown) |
| @vitejs/plugin-vue | 4.6.2 | **6.0.10** |
| @novnc/novnc | 1.6.0 | **1.7.0** |

## Breakages found and fixed

1. **SQLAlchemy 2.1 defaults `postgresql://` to psycopg3.** Added
   `psycopg[binary]`, removed `psycopg2-binary`, and ported
   `scripts/user_transfer.py` to `psycopg` + `psycopg.rows.dict_row`. No URL
   rewrites were needed in `.env`, compose, or scripts.
2. **noVNC 1.7 changed its `exports` map** to a single `./core/rfb.js`
   entry point, so `@novnc/novnc/lib/rfb.js` no longer resolves. The RangeBox
   viewer now imports the package root (`import('@novnc/novnc')`), which
   resolves to the same RFB class. noVNC 1.6 could not be bundled by Vite 8
   (CommonJS `require()` of a module with top-level await); 1.7 is required.
3. **Vite 8 uses Rolldown.** Build verified after the noVNC change; no config
   changes were needed.

## Verification

- Backend: **62 tests pass** on PostgreSQL 17.
- `pip-audit -r requirements.txt`: **0 packages with advisories**. This clears
  the last 14 Starlette findings.
- Frontend: `npm run lint` 0 errors, `npm run build` passes, `npm audit`
  **0 vulnerabilities**.
- Backend and frontend images build from clean contexts.

## Deliberately not included

- **Python 3.11 → 3.13**: runtime image change, separate wave with the
  compatibility matrix.
- **Postgres 15 → 17/18**: dump/restore rehearsal required.
- **vue-router 5, eslint 10, eslint-plugin-vue 10**: not security relevant and
  each needs its own migration. Tracked for the next tooling wave.
- **Node 24**: image and CI stay on 22 (the `versions.yaml` target); 24 is the
  next candidate.

## Rollback

Revert the commit and rebuild. The database schema is unchanged, but the
psycopg driver swap means the image must be rebuilt together with the code;
mixing a psycopg3 image with a psycopg2-era `requirements.txt` will not work.
