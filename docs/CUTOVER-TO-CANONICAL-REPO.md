# Cutover to the canonical repository

Status: the repository is renamed to `RobChaykoski/opencyberrange` and branch
protection is enabled. The remaining steps are the production host switch and
archiving the pre-cutover repository.

Target end state:

| Repository | Role |
|---|---|
| `RobChaykoski/opencyberrange` (renamed from `opencyberrange-next`) | Canonical development and production tree |
| `RobChaykoski/opencyberrange-backup` | Read-only archive and rollback point |

The canonical URLs in the documentation now resolve, and the old
`opencyberrange-next` URL redirects.

## What the cutover changed

- `scripts/upgrade-from-backup.sh` and `scripts/verify-upgrade.sh` now default
  to `origin` and fall back to the legacy `backup` remote when `origin` is
  absent. Existing hosts keep working without a flag.
- `README.md`, `README-UPGRADE.md`, `SECURITY.md`, the issue-template links,
  and the Manual-Lite upgrade guide point at the canonical repository.
- Version references move from `v2.3.0` to the current `v2.3.2` release line.
- `docs/MOVE-TO-OPENCYBER-NEXT.md` is marked historical.
- `platform/frontend/wiki/` is generated output and is deliberately not edited.
  Rebuild it with `platform/scripts/deploy-wiki.sh build` if you ship the
  checked-in tree.

## Before merging

- [x] CI is green on `cutover/canonical-repo` (merged as PR #24).
- [x] `opencyberrange-next` still contains every pre-cutover commit:
      `git rev-list --left-right --count current/main...HEAD` reports `0` on the
      left.
- [x] The pre-cutover tags exist locally and on the backup remote:
      `v2.1.0`–`v2.3.2`, `final-current-2026-11-01`, `wave-0-baseline`.
- [ ] No production host has uncommitted work
      (`git -C <checkout> status --porcelain --untracked-files=no` is empty).

## 1. Rename the repository

Completed on 2026-11-02.

In GitHub: **Settings → Repository name → `opencyberrange` → Rename**.

GitHub keeps redirects for the old `opencyberrange-next` URL, including Git
remotes and web links. Renaming preserves tags, branches, issues, PRs, secrets,
and security settings.

Then update the local clone:

```bash
git remote set-url origin https://github.com/RobChaykoski/opencyberrange.git
git remote -v
git fetch origin
```

Also update the repository description and topics so it no longer says
"staging".

## 2. Verify the rename

```bash
git ls-remote --heads --tags origin | head
curl -sI https://github.com/RobChaykoski/opencyberrange | head -n 1
curl -sI https://github.com/RobChaykoski/opencyberrange/security/advisories/new | head -n 1
```

- [x] The canonical URL returns `200`.
- [x] The old URL redirects to the canonical URL.
- [x] Private vulnerability reporting is enabled on the canonical repository.
- [x] `main` is the default branch.
- [x] Branch protection on `main` requires the backend, frontend, and compose
      checks, linear history, and resolved conversations.

## 3. Resolve Dependabot work

The pre-cutover repository had nine open Dependabot PRs; the canonical
repository has thirteen. Decide each one before archiving:

- [ ] Merge or close the canonical PRs that should land.
- [ ] Close the pre-cutover PRs that are already covered by Waves A–C, or let
      archiving close them.
- [ ] Confirm Renovate is installed on the canonical repository
      (`renovate.json` is already present).

## 4. Switch production hosts

Run these steps on each host, in order. Replace `$HOME/opencyberrange` with the
real checkout path.

```bash
cd "$HOME/opencyberrange"

# 1. Add the canonical repository as origin. If origin already exists, set its
#    URL instead.
git remote get-url origin >/dev/null 2>&1 \
  && git remote set-url origin https://github.com/RobChaykoski/opencyberrange.git \
  || git remote add origin https://github.com/RobChaykoski/opencyberrange.git

# 2. Keep the pre-cutover remote for rollback, pointed at the archive.
git remote set-url backup https://github.com/RobChaykoski/opencyberrange-backup.git 2>/dev/null || true
git remote -v
```

The deployed copy of the script may still default to `backup`. Run the new
scripts from a temporary clone, which also avoids a chicken-and-egg fetch:

```bash
git clone --depth 1 --branch main \
  https://github.com/RobChaykoski/opencyberrange.git /tmp/ocr-cutover

sudo bash /tmp/ocr-cutover/scripts/verify-upgrade.sh \
  --repo "$HOME/opencyberrange" --remote origin --branch main

sudo bash /tmp/ocr-cutover/scripts/upgrade-from-backup.sh \
  --repo "$HOME/opencyberrange" --remote origin --branch main
```

For a code-only rehearsal, add `--skip-labs --skip-rangebox` to the upgrade
command. Run the full upgrade once the dry run and verification pass.

- [ ] The upgrade completes and the backend reports healthy.
- [ ] The user count matches the pre-upgrade backup.
- [ ] The hosted manual and login work over HTTPS.
- [ ] `git -C "$HOME/opencyberrange" status -sb` is clean and tracks
      `origin/main`.
- [ ] The next scheduled upgrade on the host uses `origin` by default.

## 5. Archive the pre-cutover repository

Only after every host pulls from the canonical repository:

GitHub → `opencyberrange-backup` → **Settings → Danger Zone → Archive this
repository**.

Archiving:

- makes the repository read-only (pushes, releases, and issue changes are
  rejected);
- stops Dependabot and closes open PRs;
- keeps branches, tags, and clone access for rollback;
- can be reversed with **Unarchive**.

Checklist:

- [ ] No host, CI job, script, or bookmark still fetches
      `opencyberrange-backup` for upgrades.
- [ ] The canonical repository has every release tag you need.
- [ ] `README.md` still renders after the archive (the table already describes
      the archive role).
- [ ] The security advisory link points at the canonical repository.
- [ ] The archive action is recorded in the release notes.

## 6. Rollback

Archiving does not delete anything. To roll back:

1. Unarchive `opencyberrange-backup` in GitHub.
2. On the host, point the remote back at the backup repository.
3. Check out the last good tag (`v2.3.2` or
   `final-current-2026-11-01`).
4. Run `verify-upgrade.sh` and `upgrade-from-backup.sh` with
   `--remote backup`.

Do not force-push either repository. The archive is the rollback point, not a
scratch branch.

## 7. Post-cutover cleanup

- [ ] Update bookmarks, CI variables, deployment keys, and monitoring URLs.
- [ ] Search for stale references:
      `git grep -n 'opencyberrange-backup' -- ':!platform/frontend/wiki/**'`.
      Only historical records and the archive row should remain.
- [ ] Rebuild the checked-in wiki if you publish it:
      `bash platform/scripts/deploy-wiki.sh build`.
- [ ] Update the repository description, website, and social preview.
- [ ] Tag the cutover release (`v2.3.3` or the next release) on the canonical
      repository.
