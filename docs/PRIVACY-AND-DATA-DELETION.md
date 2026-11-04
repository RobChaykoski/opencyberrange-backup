# Privacy, Erasure, and Backups

This document describes the platform's technical controls for the GDPR right
to erasure (Article 17), the right of access/portability (Articles 15 and 20),
and the backup/restore behaviour that makes erasure durable. It is an
engineering reference, not legal advice. A privacy notice, records of
processing, and a retention schedule still need review by counsel or a DPO.

## What data exists

| Category | Storage | On erasure |
|---|---|---|
| Identity: username, email, name, student ID, organisation, avatar | `users` | Deleted |
| Credentials and security: password hash, TOTP secret, recovery codes, trusted devices, last-login IP | `users` | Deleted |
| VPN: private/public keys and client IP | `wireguard_configs` | Deleted and peer removed |
| Learning: enrolments, completions, flag attempts, quiz attempts, achievements, competition entries, completion resets | User-linked tables | Deleted |
| Lab sessions and containers | `lab_sessions` + Docker | All sessions destroyed and rows deleted |
| Survey consent state and history | `users.survey_*`, `survey_consent_events` | Deleted (cascades with the account) |
| WebSocket tickets | `ws_tickets` | Deleted |
| Activity feed | `activity_events` | Anonymised: actor, target, label, detail and IP removed |
| Invite addresses | `invite_codes.email` | Scrubbed |
| Courses owned by an instructor | `courses` | **Not deleted**; erasure is blocked until they are transferred |
| Authored labs/templates | `labs.created_by`, `exercise_templates.created_by` | Kept; author link nulled |
| Security audit stream | container logs | Retained for a short, documented period; new erasure entries do not include the erased identifier |
| Backups | `database.dump`, `users-export.json`, `erasure-ledger.jsonl` | Rotated on a 30-day default; restores re-apply the live ledger |

Downloaded certificate or transcript PDFs are generated on demand and are not
stored by the platform. Once a user downloads one, the platform cannot revoke
that copy.

## User-initiated erasure

Profile → **Privacy and data** → **Delete my account**.

The request requires:

1. the current password;
2. a live TOTP code or an unused recovery code when MFA is enabled; and
3. typing `DELETE`.

Deletion is immediate and irreversible. The UI offers a JSON data export
first. Students are deleted straight away. An instructor who owns courses
receives a `409 owned_courses` response listing the courses; an administrator
must transfer each course in **Admin → Courses → Manage → Assigned
instructor** and then the instructor can delete the account. The last usable
administrator cannot delete themselves.

## Administrator-initiated erasure

**Admin → Users → Delete** requires typing the username. It applies the same
guards and the same erasure service as the self-service path. Rejecting a
pending account also uses it.

Deleting a course is a separate action and is never part of account erasure.
That distinction protects other students' enrolments, assignments, and
achievements.

## What is retained, and why

- **Anonymised activity events.** The event type and timestamp remain for
  security and operational history; the identity, label, detail and IP are
  removed.
- **Anonymised audit records.** Administrative audit lines keep the acting
  administrator, action and timestamp. New erasure audit entries deliberately
  omit the erased person's username.
- **Authored content.** Labs and templates survive with `created_by = NULL`;
  they are course material, not account data.
- **Suppression ledger.** A keyed hash of the erased username and email is kept
  so a restore cannot resurrect the account. This is a suppression list, not a
  profile.
- **Backups.** A backup taken before the deletion can still contain the
  account until it ages out of the retention window. Restores must re-apply the
  live suppression ledger (below). The default retention is 30 days.

The current retention defaults are: activity/audit review up to 90 days and
backups 30 days. Adjust these to match the institution's retention schedule.

## Data export

`GET /api/auth/export` returns a JSON document containing the account record,
VPN metadata, courses, completions, flag attempts, quiz attempts,
achievements, lab sessions, competition entries, and activity history.
Password hashes, TOTP secrets, recovery codes, trusted-device tokens, and the
WireGuard private key are excluded.

## Suppression ledger and backups

The ledger is an append-only JSONL file at `ERASURE_LEDGER_PATH`
(default `/workbook/erasure-ledger.jsonl`). It lives on the persistent
`/workbook` volume, outside PostgreSQL, so a `pg_restore` cannot overwrite it.
Each line contains a timestamp, the actor type, and HMAC-SHA256 hashes of the
normalised username and email. Set `ERASURE_LEDGER_KEY` to a dedicated stable
key, or leave it empty to use `JWT_SECRET`. Changing the key invalidates old
entries.

### Restore procedure

A database dump can predate a deletion. After any full restore:

```bash
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  cp scripts/purge_erased_accounts.py backend:/tmp/purge_erased_accounts.py
docker compose ... exec -T backend python /tmp/purge_erased_accounts.py --dry-run
docker compose ... exec -T backend python /tmp/purge_erased_accounts.py
```

The purge utility reads the **live** ledger, finds matching accounts, and runs
the same erasure service. It does not touch Docker or WireGuard. It will refuse
to delete an instructor who still owns courses, and reports that account for
manual transfer.

### User export merge

`scripts/user_transfer.py import` consults the ledger by default and skips
erased accounts:

```bash
python /tmp/user_transfer.py import /tmp/users-export.json \
  --ledger /workbook/erasure-ledger.jsonl --dry-run
```

Use `--include-erased` only for a deliberate disaster-recovery restore; it
undoes erasure and should require a documented decision.

### Backup retention

`scripts/upgrade-from-backup.sh` copies the ledger into each backup and prunes
completed `ocr-*` backups older than 30 days after a successful upgrade. Use
`--backup-retention-days N` to change this or `0` to disable pruning. The
in-browser admin backup copies the ledger beside the dump as well.

Backups contain password hashes and personal data. Restrict access, encrypt
them at rest where possible, and delete them once the retention period ends.

## Operational checklist

- [ ] Publish a privacy notice and link it from registration and the footer.
- [ ] Record the lawful basis for each processing purpose (contract for the
      account, legitimate interest for security logs).
- [ ] Maintain a retention schedule for activity, audit, logs, and backups.
- [ ] Define the high-school/minor consent process (parental consent rules vary
      by member state).
- [ ] Keep `ERASURE_LEDGER_KEY` stable and backed up separately from the DB.
- [ ] Run a restore drill and confirm `purge_erased_accounts.py` works.
- [ ] Review the 90-day audit and 30-day backup defaults with counsel.
- [ ] Document the breach-notification and data-subject-request procedures.
