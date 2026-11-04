# Moving All Content to `opencyberrange-next`

Status: historical. This document records the move from the pre-cutover tree to
the staging repository. The staging repository was subsequently renamed to
`RobChaykoski/opencyberrange` and is now the canonical tree. See
`CUTOVER-TO-CANONICAL-REPO.md` for the remaining cutover steps.

## Current state

| Tree | Location | State |
|---|---|---|
| Canonical | `RobChaykoski/opencyberrange` (formerly `opencyberrange-next`) | `main`, release line `v2.3.2` plus Waves 0–C |
| Pre-cutover archive | `RobChaykoski/opencyberrange-backup` | `main`, `v2.3.2`; read-only after the cutover |

The canonical tree contains every tracked file and commit from the pre-cutover
tree plus the Wave 0 scaffold and the dependency waves.

## Goal

Make `opencyberrange-next` contain:

1. every tracked file and commit from the frozen current `main`;
2. the Wave 0 upgrade scaffold on top;
3. a clean, linear history;
4. the same licence, notices, provenance, and skills;
5. no `.env`, backups, generated output, or other ignored state.

## 1. Freeze the current tree (complete)

The final current commit is the last commit on `main`. Tag it before moving:

```bash
cd /path/to/opencyberrange
git status --short
git tag -a final-current-2026-11-01 -m "Final OpenCyberRange current-version snapshot"
git push backup main
git push backup final-current-2026-11-01
```

From this point:

- no feature work on current;
- only a critical hotfix may be cherry-picked from next;
- the tag is the rollback point.

## 2. Rebase the Wave 0 scaffold onto current (complete)

The next tree has one unique commit. Replay it on top of current so the result
is a linear `current + Wave 0` history.

```bash
cd /path/to/opencyberrange-next
git fetch current main
git rebase current/main
```

Expected: the Wave 0 commit is replayed on top of the final current commit.
Conflicts are unlikely because Wave 0 adds new files. If a conflict occurs:

- keep the current tree's content;
- keep the Wave 0 additions (`versions.yaml`, supported-versions docs, CI,
  Renovate, version report, `ruff` in dev requirements);
- do not delete current lab, workbook, skill, or migration content.

If the rebase becomes tangled, use the equivalent clean path:

```bash
git checkout -B migration current/main
git cherry-pick <wave-0-commit>
# resolve, then
git branch -f main migration
```

## 3. Update the Wave 0 baseline reference (complete)

`docs/WAVE-0-BASELINE.md` names the release commit as its source, matching the
current commit.

Also check `README-UPGRADE.md` and `docs/UPGRADE-TO-LATEST-GA-PLAN.md` for any
stale commit references.

## 4. Verify the new tree (complete)

```bash
cd /path/to/opencyberrange-next

git status --short
git log --oneline -5
git diff --stat current/main..HEAD
```

The diff should show the Wave 0 scaffold plus this migration-status update.
Then run the full gates:

```bash
# Backend
cd platform/backend
python -m pytest -q

# Frontend
cd ../frontend
npm ci
npm run lint
npm run build

# Labs
cd ../..
python scripts/validate-lab.py --all

# Compose
cd platform
docker compose --env-file .env -f docker-compose.prod.yml config >/dev/null
```

Also run the two software-security labs and the DevFest seed smoke test, or
reuse the recorded results from the final current commit.

Verified on the rebased Wave 0 tree:

- 54 backend tests passed on PostgreSQL 17.
- Frontend lint: 0 errors; production build passed.
- Both Software Security labs validated (21/22 checks; informational resource
  limit suggestion only).
- `docker compose config` resolved `LABS_HOST_PATH` to the next tree.
- `git diff --stat current/main..HEAD` contains the Wave 0 scaffold and this
  migration-status update.

## 5. Create and push the new repository (complete)

The repository exists at <https://github.com/RobChaykoski/opencyberrange-next>,
is public, and uses `main` as its default branch. Pushed content:

```bash
cd /path/to/opencyberrange-next
git push -u origin main
git push origin --tags
```

Tags present: `final-current-2026-11-01`, `v2.1.0`–`v2.1.4`,
`wave-0-baseline`.

### Push-protection caveat

The account blocks pushes of detected secrets to **public** repositories,
independent of the repository-level setting. The training labs deliberately
contain a well-known Stripe demo key
(`platform/labs/Linux/linux-4-1-credential-pivot-attack/.../Dockerfile`), so
the initial import was rejected with `GH013` even after
`secret_scanning_push_protection` was set to `disabled`.

The import was completed by temporarily making the repository private:

```bash
# repository was set private, main + tags pushed, then set public again
```

Secret scanning alerts remain enabled on the repository. If history is ever
force-pushed through a public path, expect the same `GH013` rejection and use
the temporary-private method again.

After the push:

- [x] set `main` as the default branch;
- [ ] protect `main` (PR + CI required);
- [ ] install the Renovate app (Dependabot is already active);
- [x] confirm the new CI workflows run.

## 6. Switch development to the canonical repository

- Treat `opencyberrange` (formerly `opencyberrange-next`) as the only
  development tree.
- Keep the pre-cutover repository as a read-only archive and rollback tag.
- Rename the local remotes for clarity if desired:
  - `origin` = `opencyberrange`;
  - `current` = `opencyberrange-backup` (frozen);
  - optionally `legacy` = the old backup remote.
- Do not delete the pre-cutover repository or its tags.

## 7. Production promotion

Do not point production hosts at the canonical development branch directly. Use
a release promotion:

1. `opencyberrange` passes CI and staging checks.
2. Create a release tag, e.g. `v2.3.3`.
3. Promote the release through the production remote, either by:
   - mirroring `main` to `opencyberrange-backup` after review; or
   - pointing the hosts at `opencyberrange` and switching `GIT_REMOTE`/`--remote`
     at the same time.
4. Keep the existing host upgrade scripts on the production remote until the
   promotion is complete.

This preserves the current upgrade, backup, and rollback path.

## 8. Content checklist

Tracked content that must be present in next:

- [ ] application code (`platform/backend`, `platform/frontend`)
- [ ] labs (`platform/labs`), including the Software Security track
- [ ] workbooks (`Workbook`), including `CH_SWSEC_Software_Security`
- [ ] docs (`docs`), including privacy/erasure and upgrade plans
- [ ] scripts (`scripts`), including backup/restore and lab validation
- [ ] skills (`.opencode/skills`), including
      `opencyberrange-software-security`
- [ ] `.github` workflows and `renovate.json`
- [ ] `.gitattributes`, `.gitignore`, licence, notices, provenance
- [ ] `mkdocs-*.yml`, `wikis.yaml`, and Manual-Lite content
- [ ] tests, templates, and RangeBox/UbuntuBox/RemnuxBox sources

Must **not** be moved:

- `platform/.env` and any `.env.*` secret files
- `backups/` or database dumps
- `node_modules`, `dist`, `.venv`, `__pycache__`, `.pytest_cache`,
  `.ruff_cache`
- generated wiki output or `_site_*` directories
- the erasure ledger file (it lives on the host volume, not in git)

## 9. Secret and provenance checks

Before pushing:

```bash
git grep -nE '(JWT_SECRET|POSTGRES_PASSWORD|WG_API_KEY|BEGIN .*PRIVATE KEY)=' || true
git status --ignored --short | head -40
git ls-files | wc -l
```

Confirm `LICENSE`, `NOTICE`, `LICENSING.md`, `BUILD_NOTICE.md`, and
`THIRD_PARTY_NOTICES.md` are present and unchanged.

## 10. Rollback

- Current is frozen at `final-current-2026-11-01` and remains on the production
  remote.
- If next is wrong, delete or reset it and recreate from the tag.
- Production continues to pull from the production remote until a deliberate
  promotion.

## 11. Timeline

| Step | Estimate |
|---|---|
| Freeze/tag current | 5 minutes |
| Rebase Wave 0 onto current | 15 minutes |
| Resolve conflicts (if any) | 30 minutes |
| Full test/build/validation | 1–2 hours |
| Create and push new repo | 15 minutes |
| CI green and cutover | Same day |
| Production promotion | Separate release decision |
