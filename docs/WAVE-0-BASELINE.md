# Wave 0 Baseline

Date: 2026-11-01

This records the passing state before any application dependency is changed.

## Environment

| Item | Value |
|---|---|
| Source | `RobChaykoski/opencyberrange-backup` at `8be1e9d` |
| Backend test database | PostgreSQL 17 (local container) |
| Backend Python | 3.11.9 (existing venv) |
| Frontend Node | v24.22.1 (workstation); CI baseline uses Node 18 |
| Compose | `platform/docker-compose.prod.yml` |

## Results

| Gate | Result |
|---|---|
| Backend test suite | **54 passed** |
| `ruff check app` | 119 legacy findings; non-blocking in CI until cleanup |
| Frontend `npm ci` | Passed |
| Frontend `npm run lint` | 0 errors, 144 existing warnings |
| Frontend `npm run build` | Passed |
| `docker compose config` | Passed with CI environment variables |
| Version inventory | `python scripts/report-versions.py --platform-only` works |

## Known baseline warnings

- Ruff: 119 findings, mostly unused imports (`F401`). The existing
  `pyproject.toml` explicitly asks for incremental cleanup rather than a bulk
  `--fix`, so the Wave 0 CI step is non-blocking.
- Frontend lint: 144 warnings, 0 errors. These are pre-existing
  `no-unused-vars` warnings.
- `npm ci` reports install-script approval warnings for `esbuild` on this
  workstation; the lockfile and build are unaffected.
- MkDocs 2.0 is incompatible with the installed Material theme; docs build
  validation stays on MkDocs 1.6.1 for now.

## Commands

```bash
# Backend
cd platform/backend
TEST_DATABASE_URL=postgresql://ocr_test:ocr_test@127.0.0.1:5432/ocr_test pytest -q

# Frontend
cd platform/frontend
npm ci
npm run lint
npm run build

# Compose
cd platform
docker compose -f docker-compose.prod.yml config >/dev/null

# Inventory
python scripts/report-versions.py --platform-only
```

## Next gate

Wave 1 changes only the Python/Node runtime images and frontend build
toolchain. Do not mix application package upgrades into Wave 1.
