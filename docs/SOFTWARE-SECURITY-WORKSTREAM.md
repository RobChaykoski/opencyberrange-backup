# Software Security Workstream

Status: starter track implemented; pending deployment and browser rehearsal.
Target: the canonical production tree.

## 1. Goal

Build a software-security course that starts with reading and reasoning about
code, then moves into writing exploits against safe, local targets. The first
milestone is two browser-first exercises that can join the GDG Windsor DevFest
initial competition alongside the existing OSINT challenge.

Constraints:

- DevFest participants may have no terminal, no VPN, and no security background.
- Each DevFest exercise should take 10–20 minutes and work entirely in the lab
  browser.
- Targets must be fictional, deterministic, isolated, and safe to break.
- Later exploit-writing levels can require a RangeBox or terminal, but the
  DevFest pair must not.
- No real personal data, real credentials, or external targets.

## 2. Course arc

Proposed track: **Software Security**.

| Level | Theme | Example skills | Tools |
|---|---|---|---|
| 1 | Reading Code for Bugs | Source review, hidden routes, client-side secrets, trust boundaries | Browser |
| 2 | Injection and Exploitation | Command injection, SQL injection, input validation, simple payloads | Browser or terminal |
| 3 | Authentication and Authorization | IDOR, broken access control, session flaws, privilege checks | Browser or terminal |
| 4 | Memory Safety and Exploit Development | C bug classes, crash triage, offsets, a first Python exploit script | RangeBox |
| 5 | Capstone Exploit Development | End-to-end exploit, reliability, mitigation, disclosure write-up | RangeBox |

Each level should have two to four labs plus a chapter review. Level 4 is where
"writing an exploit" becomes literal; it should not be forced into the DevFest
beginner pair.

## 3. DevFest MVP: two exercises

Both exercises should be `difficulty: beginner`, browser-only, and independent
of each other so a participant can attempt either one first.

### Exercise 1 — Hidden Export Route

- **Slug:** `software-security-1-1-hidden-export-route`
- **Working name:** DevFest Speaker Portal
- **Concept:** client-side code is public; a hidden route and token in shipped
  JavaScript are not access control.
- **Flow:**
  1. Open the fictional DevFest speaker portal.
  2. View the page source or open the linked JavaScript file.
  3. Find a developer comment with an export route and token.
  4. Open the route with the token and read the flag.
- **Flag:** `OCR{cl13nt_s1d3_s3cr3ts_4r3_publ1c}` (placeholder; finalize before
  publishing).
- **Test steps:**
  - `GET /` returns 200.
  - `GET /static/app.js` contains the export route.
  - `GET /admin/export?token=...` contains the flag.
- **Teaching point:** shipping a secret to the browser makes it public; the
  server must enforce authorization.

### Exercise 2 — Diagnostics Command Injection

- **Slug:** `software-security-2-1-diagnostics-command-injection`
- **Working name:** DevFest Network Diagnostics
- **Concept:** untrusted input passed to a shell lets an attacker run another
  command.
- **Flow:**
  1. Open the diagnostics page.
  2. Run a normal host lookup.
  3. Try a shell separator and read the flag file.
  4. Explain how to remove the shell and validate input.
- **Flag:** `OCR{sh3ll_1nj3ct10n_1s_4_bug}` (placeholder).
- **Test steps:**
  - `GET /lookup?host=127.0.0.1` returns 200.
  - `GET /lookup?host=127.0.0.1%3Bcat%20/tmp/flag` contains the flag.
- **Teaching point:** use argument arrays, avoid `shell=True`, allowlist input,
  and run with least privilege.

### Shared target

One dependency-free Python standard-library app can serve both modes:

- `LAB_MODE=code_review` — portal, JavaScript, hidden export route.
- `LAB_MODE=command_injection` — diagnostics form and shell-backed lookup.

Each lab gets its own container, flag, hostname, and `ip_offset`. Run read-only,
drop all capabilities, use a small tmpfs, and keep the target on the isolated
lab network. The command-injection lab intentionally executes shell input
inside its own container; that is the exercise, not a platform escape.

## 4. DevFest competition integration

The existing competition seed creates one OSINT lab. The initial competition
should contain three short exercises:

| Sort | Lab | Time |
|---|---|---|
| 0 | `high-school-12-1-devfest-community-portal` | ~25 min |
| 1 | `software-security-1-1-hidden-export-route` | ~15 min |
| 2 | `software-security-2-1-diagnostics-command-injection` | ~15 min |

Update `seed_devfest_competition.py` to:

- keep the existing OSINT lab;
- add the two software-security labs when they exist;
- be idempotent for an existing competition: add any missing labs instead of
  returning early;
- keep the event window overridable with `DEVFEST_START` / `DEVFEST_END`.

Publish the two labs (`visibility: public`) only after validation and a manual
browser solve. Keep them `draft` while authoring.

## 5. Platform changes required

- Add the `software-security` track and levels 1–5 to:
  - `platform/backend/app/scripts/seed_curriculum.py`
  - `platform/scripts/seed_curriculum.py`
- Add `software-security` to `scripts/validate-lab.py` `KNOWN_TRACK_SLUGS`.
- Add `software-security: Software Security` to `scripts/new-lab.py`
  `TRACK_DIRS`.
- Update `platform/scripts/discover_labs.py` to parse compound track slugs the
  same way the backend discoverer already does.
- Add `software-security` to `wikis.yaml` and a new `mkdocs-swsec.yml`.
- Add `Workbook/CH_SWSEC_Software_Security/` with introduction, two exercise
  pages, and a chapter review.
- Use an existing track icon (`web` or `brain`) for the first release; no new
  icon asset is required.
- Add the two lab slugs to the DevFest seed after they validate.

## 6. Workbook outline

`Workbook/CH_SWSEC_Software_Security/`

- `00_Introduction.md` — what software security is, safe lab rules, browser-only
  expectations, ethics.
- `01_Hidden_Export_Route.md` — source review, devtools/view-source, hidden
  route, why client-side checks fail.
- `02_Diagnostics_Command_Injection.md` — input handling, shell injection,
  payload, remediation.
- `03_Chapter_Review.md` — self-assessment, answer key, remediation checklist,
  next steps toward Level 3/4.

Each exercise page follows the existing workbook pattern: Before You Begin →
Scenario → Objectives → Background → Walkthrough → What Just Happened → Analysis
Questions → Defensive Takeaways → If You Get Stuck → Further Reading.

## 7. Acceptance criteria

- [ ] Both labs pass `python scripts/validate-lab.py <lab>`.
- [ ] Both Docker images build and the flags are retrievable by the documented
      test steps.
- [ ] A beginner can solve each in 15 minutes or less using only the browser.
- [ ] Hints scaffold without giving away the flag in the first hint.
- [ ] The DevFest competition seed includes all three labs and is idempotent.
- [ ] The workbook builds and the new track appears in the catalogue.
- [ ] No real data, external targets, or host mounts are used.
- [ ] The command-injection container is read-only, drops capabilities, and
      keeps the flag in tmpfs.

## 8. Timeline

| Window | Work |
|---|---|
| Day 1–2 | Track/seed/discovery scaffolding; shared target skeleton |
| Day 3–5 | Exercise 1 app, workbook page, validation, Docker build |
| Day 6–8 | Exercise 2 app, workbook page, validation, Docker build |
| Day 9–10 | Competition seed update, dry run, publish drafts, browser test |
| Before 2026-11-21 | Buffer, accessibility/polish, event rehearsal |

## 9. Deferred to later levels

- C buffer overflow and memory-safety exploit development.
- Writing a reusable Python exploit script with offsets and payload delivery.
- Mitigations: ASLR, NX, stack canaries, and why they change the exploit.
- Responsible disclosure and write-up.
- A capstone that combines source review, exploitation, and remediation.

## 10. Decisions and status

Locked:

1. Dedicated `software-security` track.
2. Code review + command injection as the DevFest starter pair.
3. Existing OSINT lab plus both new labs in the initial competition.
4. Both draft labs were built and validated.

Implemented:

- Track and levels 1–5 in both curriculum seeds.
- Two public labs: `software-security-1-1-hidden-export-route` and
  `software-security-2-1-diagnostics-command-injection`.
- Shared dependency-free target under `platform/labs/_swsec_shared`.
- Workbook chapter, wiki config, and `wikis.yaml` entry.
- DevFest seed now includes all three labs and adds missing labs to an existing
  competition.
- `opencyberrange-software-security` skill with plain-language concepts and a
  bad-practices-to-exploits catalogue.

Verification performed:

- Both labs pass `scripts/validate-lab.py` (21/22 checks; one informational
  resource-limit suggestion).
- Both compose files build.
- Code-review route and command-injection payload were exercised in Docker.
- Seed/discovery/competition smoke test: 5 levels, 2 labs, 3 competition labs.

Not yet done:

- Browser-based manual solve and event rehearsal.
- Deployment of this commit to the live server.
- Levels 3–5 lab content and the exploit-development workbook.
- A dedicated `mkdocs` build check (the local MkDocs 2.0 install is incompatible
  with Material; the config uses the same structure as the existing manuals).
