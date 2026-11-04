# OpenCyberRange

> **Original project and attribution**
>
> OpenCyberRange is based on the original
> [Open Cyber Range](https://opencyberrange.com/) (OCR-Lite) project, designed
> and built by **[Lewis Heuermann](https://github.com/syntaxoverride)** and
> published at
> [syntaxoverride/opencyberrange](https://github.com/syntaxoverride/opencyberrange).
> Lewis is a cybersecurity and data analytics professor and a Capture the Flag
> coach. **This project would not exist without his original hard work.**
>
> This repository is an independent updated build maintained by Robert
> Chaykoski. It is not an official upstream release and is not endorsed by the
> original author. See [BUILD_NOTICE.md](BUILD_NOTICE.md) for the full notice.
> The original copyright and PolyForm Noncommercial licence remain in force.

[![Labs](https://img.shields.io/badge/labs-148-blue)](platform/labs/)
[![Tracks](https://img.shields.io/badge/tracks-11-green)](platform/labs/)
[![Platform](https://img.shields.io/badge/platform-Docker%20%2B%20WireGuard-orange)](Manual-Lite/00_Server_Deployment/06_Architecture.md)
[![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial%201.0.0-blue)](LICENSE)
[![AI-assisted](https://img.shields.io/badge/AI-assisted%20build-8b5cf6)](#ai-assistance-disclosure)

A self-hosted cybersecurity training platform that deploys hands-on exercises inside isolated Docker containers. Students connect over WireGuard VPN, solve challenges across instructor-defined tracks, and submit flags for automated scoring. The platform ships with foundational exercises spanning penetration testing, network foundations and forensics, web exploitation, malware analysis, OT/ICS security, AI security, and open-source intelligence (OSINT).

Students also get a profile with completion statistics, certificates, achievements, and a downloadable PDF transcript. They can download their account data or permanently delete their account from the privacy panel; the erasure suppression ledger and backup workflow keep a restore from resurrecting a deleted account. Instructors and administrators manage courses, progress, and the platform from the same interface.

## Measurable outcomes

These are current, checkable counts from this repository and metrics the platform records itself. They describe what learners and instructors can measure; they are not claims about learning ability.

| Outcome | How it is measured | Baseline in this repository |
|---|---|---|
| Breadth of hands-on practice | Runnable exercises, tracks, and levels | **148 exercises** across **11 tracks** and **51 levels** |
| Guided lab instruction | Workbook walkthroughs and analysis questions | **164 workbook pages**, **111 analysis sections**, **407 analysis questions** |
| Supported practice | Hints available and hint usage recorded per completion | **500+ hints**; hints used are stored with each completion |
| Automated verification | Per-lab validation checks and flag checks | **650+ validation checks**; flags are stored as hashes |
| Skill progression | Sequential level completion and level certificates | Level gates and **certificates for each completed level** |
| Course delivery | Assignments, completion counts, and scoreboard | Per-student completion, attempt, hint, and time records |
| Recognition | Achievement and competition scoring signals | Completion, no-hint, first-attempt, speed, and first-blood signals |
| Learner evidence | Profile, transcript, and reports | PDF transcript, completion matrix, and per-course reports |
| Session isolation | Network separation per learner | One `/24` per session plus WireGuard access |

### Release and repositories

| Repository | Purpose | State |
|---|---|---|
| [`opencyberrange`](https://github.com/RobChaykoski/opencyberrange) | Production and development (canonical) | `v2.3.2`, CI green |
| [`opencyberrange-backup`](https://github.com/RobChaykoski/opencyberrange-backup) | Read-only archive of the pre-cutover tree | `v2.3.2`; archived at cutover |

This repository is the only development tree. It contains all history from the
pre-cutover tree plus the upgrade scaffold and dependency waves. See
`docs/MOVE-TO-OPENCYBER-NEXT.md` and `docs/CUTOVER-TO-CANONICAL-REPO.md` for the
migration and cutover trail.

## AI assistance disclosure

**This updated build was created with AI assistance.** AI tools helped draft
code, tests, documentation, workbook content, curriculum material, and design
guidance. A human maintainer reviewed and takes responsibility for the changes,
but AI-assisted output can contain errors or omissions. Verify commands, lab
instructions, security controls, and licence obligations before relying on them
in production.

See [BUILD_NOTICE.md](BUILD_NOTICE.md#ai-assistance-disclosure) for the
build-specific disclosure and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
for the open-source attribution inventory.

![The Ops Center dashboard](docs/img/dashboard.png)


## What it looks like

**Exercise catalogue.** Tracks group exercises into levels; a level unlocks as
the one before it is completed.

![Browsing a track](docs/img/track.png)

**Working an exercise.** Every exercise opens with its scenario, its
objectives, a link to the workbook, and the box that takes the flag.

![An exercise open](docs/img/exercise.png)

**Courses.** Assign exercises to a class, set the weeks, and track who has
finished what.

![Courses](docs/img/courses.png)

**Administration.** Users, sessions, VPN peers and platform settings in one
panel.

![Admin panel](docs/img/admin.png)

![Platform settings](docs/img/settings.png)

**Profile and records.** Every student has a profile with an avatar, completion
stats, earned certificates, track progress, completion details, achievements,
and a downloadable PDF transcript.

**Celebration Wall.** A shared recognition page for recent wins. It is a
spotlight, not a public leaderboard: individual badge counts and ranks are not
shown. Learners choose whether their wins show their real name, their username,
or "Anonymous participant", and can opt out of the public wall at any time while
still seeing their own private corner.

![Celebration Wall](docs/img/celebration-wall.png)

**Special competitions.** Instructors and admins can open opt-in, time-boxed
events using selected exercises. The event uses the existing lab scoring rules
(completion, no-hint, first-attempt, speed, and competition first blood).
Only solves during the event window count. Learners choose to join, can leave
at any time, and see a dedicated event leaderboard. The same name preference
applies: real name, username, or "Anonymous participant".

Competitions are separate from course grades and the learning record; they are
not used for progression, discipline, or public ranking of learning outcomes.
Learners can **practise without joining**, and joining only affects the event
leaderboard. Organizers get a dedicated competition dashboard with total
participants, new sign-ups, existing opt-ins, and a copyable sign-up link.

## Included tracks

| Track | Labs | Focus |
|-------|------|-------|
| Windows Penetration Testing | 53 | Enumeration, SMB, RDP, WinRM, MSSQL, LDAP, credential reuse |
| Linux Fundamentals | 37 | Service enumeration, SSH, privilege escalation, pivoting, detection |
| Web Application Security | 16 | Reconnaissance, injection, traversal, API and authentication testing |
| Network Security | 16 | Network foundations (ping, DNS), traffic analysis, protocol attacks, firewalls, exfiltration |
| Malware Analysis | 8 | Static triage, reversing, C2 traffic, document and attachment analysis |
| OT/ICS Security | 1 | Modbus enumeration and register analysis |
| AI Hacking | 3 | Prompt injection, jailbreak policy bypass, indirect prompt injection |
| OSINT | 4 | Public-surface mapping, metadata, image steganography, source-code and public-repository leaks |
| **High School Cybersecurity** | **6** | Browser-first Grades 9–12 pathway; RangeBox basics, defensive logs, and the Grade 12 DevFest community portal |
| Software Security | 2 | Source review, hidden routes, command injection, and remediation |
| Digital Forensics | 2 | Memory analysis and VoIP network evidence reconstruction |
| **Total** | **148** | **11 tracks · 51 levels** |

## Network Foundations stream

The **Network Security** track opens with a beginner **Network Foundations**
level for students who have never used a terminal:

- **Ping Basics** — reachability, latency, packet loss, and why a reply is not a
  service check.
- **DNS Basics** — A, CNAME, MX, and TXT records, queried directly against an
  authoritative lab server.
- **Name or Network?** — a troubleshooting capstone that separates a stale name
  from a dead host and a stopped service.

The matching workbook chapter is **CH N0 -- Network Foundations**.

## AI Hacking stream

The **AI Hacking** track starts with a beginner module, **AI Security
Foundations**, containing three labs:

- **Prompt Injection Basics** — override a mock assistant's hidden instructions.
- **Jailbreak Policy Bypass** — move past a keyword filter with role-play and
  authority framing.
- **Indirect Prompt Injection** — plant instructions in a support ticket that a
  summariser reads.

Each lab uses a deterministic, dependency-free mock assistant inside the lab
network. No external model, API key, or internet access is required. The next
levels — instruction hierarchy, RAG/data exposure, agent tool abuse, model
supply chain, and an AI-assisted capstone — are defined in the curriculum and
will appear as their labs are published.

## OSINT stream

The **OSINT** track teaches students to work from the outside in. The target is
**Kestrel Ridge**, a fictional company with a simulated intranet, a public
employee badge, and a public code trail:

- **The Public Footprint** — map a staff intranet, read `robots.txt`, and find a
  flag in a review page's HTML source.
- **Badge Photo Intelligence** — inspect PNG metadata, then extract a flag from
  the least-significant bits of the blue channel. The exercise ships with a
  dependency-free Python extractor, a browser-based extractor for shared or
  low-tooling devices, and also works with `zsteg`.
- **The Developer's Trail** — fetch a static JavaScript asset and recover a
  staging token left in a developer comment. This exercise also includes a
  bonus flag hidden in the public OpenCyberRange repository.
- **The Public Homepage** — treat a live public site (`www.swocts.com`) as an
  OSINT source, search its document metadata, and find the flag left in the
  page head. A local mirror is available for offline practice.

![The OSINT track](docs/img/osint-track.png)

![Badge Photo Intelligence workbook](docs/img/osint-workbook.png)

The live SWOCTS exercise expects the meta tag documented in
[`platform/labs/OSINT/_shared/leaks/swocts-source-snippet.md`](platform/labs/OSINT/_shared/leaks/swocts-source-snippet.md).
The GitHub bonus flag is discoverable by searching the public repository for
`Kestrel Ridge` or `KR-0421`.

The matching workbook chapters are **CH OSINT1 -- Digital Footprint
Foundations** and **CH OSINT2 -- Code and Sources**. The RangeBox, UbuntuBox,
and RemnuxBox images include the supporting tooling: `exiftool`, `binwalk`,
`foremost`, `steghide`, `pngcheck`, `zsteg`, ImageMagick, and Python Pillow.

Completing the track unlocks OSINT-specific achievements, seeded alongside the
existing learning ladder: **Signal in the Noise**, **Digital Footprint**,
**Metadata Miner**, **Open Source Operative**, **Clean Footprint**, and
**First-Pass Analyst**. They are course-scoped, so a student earns them in any
course that assigns the OSINT exercises.

## High School pathway · Grades 9–12

The **High School Cybersecurity** track is a browser-first pathway for students
who are curious but may be new to the field:

| Grade | Focus |
|---|---|
| 9 | RangeBox basics and file discovery |
| 10 | Networks, HTTP responses, and browser source |
| 11 | Defensive security: logs, suspicious requests, and evidence |
| 12 | Applied cybersecurity and community event challenges |

The Grade 11 **RangeBox Log Detective** exercise introduces defensive security:
students read a short web access log, identify repeated probing from one source,
and explain the evidence before submitting a training token. It uses the same
browser-first RangeBox target as the Grade 9 and 10 exercises.

The Grade 12 **DevFest Community Portal** exercise is a gentle OSINT challenge
themed around [DevFest Windsor-Essex 2026](https://wedevfest.com) on
November 21, 2026. SWOCTS is a community partner. Students open a fictional
DevFest speaker profile, download a slide export, and read the PNG metadata in
the browser. No terminal or prior experience is required, hints are expected,
and students can practise without joining the competition.

The live DevFest competition can be created after discovering the lab:

```bash
docker compose exec backend python /app/app/scripts/seed_devfest_competition.py
```

The script creates an opt-in **Windsor-Essex DevFest 2026** event and prints the
new-participant sign-up link. Existing learners can use the competition page's
**Join event** button; new accounts created through the sign-up link are marked
as **New sign-up** on the organizer dashboard.

## VPN, MFA, and secret handling

- **WireGuard setup** supports downloading the `ocr-vpn.conf` file and an
  on-demand **QR code** for the WireGuard mobile apps. The QR contains the
  private key, so it is only generated after a click, is not cached
  (`Cache-Control: no-store`), and includes an on-screen warning not to share it.
- **TOTP enrollment** returns a scannable QR code plus the manual secret and
  provisioning URI. The QR is generated server-side, so the browser does not
  need a QR library.
- Production installations should set `WG_SERVER_ENDPOINT`,
  `WG_SERVER_PUBLIC_KEY`, `WG_API_URL`, and `WG_API_KEY` through the setup
  script or `.env`. Placeholder values such as `dummy` or a loopback endpoint
  are fine for UI testing but will not produce a working tunnel.

## Free security checks

The repository includes GitHub-native checks that need no third-party account
or repository secret:

- **Dependabot** — weekly dependency and Docker base-image update PRs.
- **CodeQL** — Python and JavaScript/TypeScript static analysis.
- **Trivy** — filesystem vulnerability, secret, and configuration scanning.
- **Dependency audit** — `pip-audit` and `npm audit --omit=dev` on every pull
  request and weekly.

Current status at `v2.3.2`: `pip-audit` reports **0 packages with advisories**
and `npm audit` reports **0 vulnerabilities**. The remediation trail is in the
`WAVE-A`, `WAVE-B`, and `WAVE-C` documents in `docs/`.

Findings appear in the repository's **Security** tab. Code scanning on a public
repository is free; a private repository needs GitHub Advanced Security for the
same feature.

Snyk Free is also available, but it requires a Snyk account and `SNYK_TOKEN`, so
it is not part of the default workflow. No scanner is a compliance certificate:
retention, access control, backups, incident response, and privacy reviews still
need to be documented separately.

For vulnerability reporting, see [SECURITY.md](SECURITY.md).

## Profile, certificates, and transcripts

The student profile is the record of completed work:

- Upload or remove an avatar; the browser resizes it before saving.
- View every earned certificate and open its printable certificate page.
- Track progress by track and level, with completion counts and certified-level
  markers.
- Expand the completion table to see every solved exercise, date, attempts, and
  hints used.
- See course achievements earned in enrolled courses.
- Download a PDF transcript containing identity details, completion totals,
  certificates, track progress, completed exercises, and achievements.

## Inclusive learning and privacy

The platform is designed for mixed-confidence learners, shared devices, and
classrooms where not every student has the same hardware:

- **Synthetic content only.** The OSINT personas, badges, tokens, and flags are
  fictional. No real employee data, credentials, or live third-party systems are
  required. The public-homepage exercise uses the organisation's own site and a
  local mirror; the workbook tells learners not to probe unrelated sites.
- **More than one access route.** The image-steganography exercise supports
  `zsteg`, a dependency-free Python extractor, and a browser-based extractor for
  Chromebooks, tablets, and shared computers. RangeBox, UbuntuBox, and RemnuxBox
  ship the supporting tools.
- **No public ranking.** The Celebration Wall shows recent wins and a
  non-ranked spotlight. It does not publish individual badge counts or ranks.
  Learners choose a real-name, username, or anonymous label, and can opt out via
  “Show me on the wall”; opted-out users still see their own private corner.
  Admin diagnostic accounts are excluded.
- **Data minimisation.** The wall exposes only a display name, the latest badge,
  and a relative timestamp. It does not expose email addresses, student IDs, or
  avatars.
- **Optional surveys, explicit consent.** Platform and usage surveys are
  off by default. Profile → **Surveys** shows the versioned privacy statement
  before consent is recorded, keeps an append-only consent history, and allows
  withdrawal at any time. Survey consent covers platform feedback only; it does
  not permit collection of passwords, grades, lab flags, or sensitive personal
  data. See [Survey privacy and consent](docs/SURVEY-PRIVACY.md).
- **Learning-impact stance.** Completion, time, and badge counts are activity
  signals, not measures of ability. The platform does not use them for public
  rankings, hiring, promotion, or discipline.
- **Accessibility.** New pages use semantic headings, labelled controls, visible
  focus, reduced-motion handling, and the existing dark/light theme tokens.
  Workbook images carry alt text, and the browser extractor works without a
  local terminal.

The screenshots in this README use a temporary synthetic account and temporary
demo records. No real learner names, emails, or records are shown.

## Building workbooks and labs

The workbook wiki and lab images are build artifacts, not source files.

- `scripts/build-wiki.sh` builds every track wiki, the reference manual, and
  any course wikis into the `wiki_data` volume. The frontend mounts that volume
  read-only; the frontend image no longer bakes HTML.
- `scripts/prebuild-labs.sh --changed` builds only labs whose source hash or
  stable image tag changed. `--all` forces a full rebuild.
- `scripts/verify-lab-builds.sh` validates every lab compose file, checks the
  stable `ocr-lab/<slug>-<service>:latest` images, and verifies workbook links
  against the running frontend.
- `scripts/build-assets.sh all` runs the wiki build, the changed-lab prebuild,
  and the verification pass.

The lab build manifest lives at `scripts/.lab-build-manifest.json` and is
generated, not committed. Set `LAB_ALLOW_ON_DEMAND_BUILD=false` in production
so a missing image fails with a clear "run prebuild-labs.sh" message instead of
building during a student spawn.

## Security and operations

### Authentication

- Username/password login issues a signed JWT with a unique `jti` claim. Tokens
  expire after `JWT_EXPIRATION_HOURS` (24-hour default) and are checked against
  a persistent revocation table on every request, so logout and admin
  revocation take effect across workers.
- Roles are enforced server-side: **student**, **instructor**, and **admin**.
  Admin impersonation is read-only and blocked from mutating data.
- Optional MFA supports TOTP and ten single-use recovery codes. Recovery codes
  are stored as hashes, not plaintext.
- Login is rate-limited to 10 attempts per minute per IP. Five failed attempts
  lock an account for 30 minutes. Registration is limited to 5/minute,
  30/hour, and 100/day per IP, with a documented relaxation during live
  competitions.
- Registration can require administrator approval and, optionally, a valid
  invite code. Instructor and administrator passwords must meet stricter
  complexity rules.

### Password storage

- New passwords are hashed with **Argon2id** through `pwdlib`.
- Legacy **bcrypt** hashes still verify; a successful login transparently
  rewrites them to Argon2id.
- Plaintext passwords are never stored. Password hashes, TOTP secrets,
  recovery codes, trusted-device tokens, and WireGuard private keys are
  excluded from the user data export.

### Backup strategy

- A complete backup includes the PostgreSQL dump, `.env`, compose file, TLS
  certificates, and the erasure suppression ledger.
- Backups contain password hashes and personal data. Keep them private, encrypt
  them at rest where possible, and delete them when the retention period ends.
- The default retention is **30 days**. `upgrade-from-backup.sh` copies the
  ledger into each backup and prunes older completed backups; use
  `--backup-retention-days N` to change the window or `0` to disable pruning.
- After a restore, re-apply the **live** erasure ledger with
  `scripts/purge_erased_accounts.py`. Otherwise an older dump could resurrect a
  deleted account. `user_transfer.py import` consults the ledger by default.
- Full procedure: [Privacy, Erasure, and Backups](docs/PRIVACY-AND-DATA-DELETION.md)
  and the [Docker Compose Deployment Manual](Manual-Lite/00_Server_Deployment/08_Docker_Deploy_Manual.md).

### VPN isolation

- Each learner receives a WireGuard peer on `10.0.0.x` and reaches only lab
  networks under `10.100.0.0/16`. Each session gets its own `/24`.
- The firewall blocks the lab and RangeBox subnets from external interfaces and
  from the host management LAN. This isolation is re-applied on backend start
  and persisted for reboot.
- Lab traffic cannot route between different learners' session networks. The
  Peer Manager API is internal-only; do not expose port 5000.
- WireGuard private keys are encrypted at rest with `WG_ENCRYPTION_KEY`. VPN
  configs and QR codes are generated on demand and marked `no-store`.
- Open `51820/udp` only when students use the VPN. See the
  [Architecture guide](Manual-Lite/00_Server_Deployment/06_Architecture.md).

### Container isolation

- Every lab session gets its own Docker bridge network and dedicated `/24`;
  services attach only to that session network, which is removed when the lab
  stops.
- The platform applies default per-service CPU and memory caps when a lab does
  not declare its own, with no swap. RangeBox desktops are separately capped and
  run with a PID limit.
- Lab definitions routinely add defence in depth: `cap_drop: ALL`,
  `security_opt: no-new-privileges`, read-only root filesystems with `tmpfs`,
  and non-root users where the image supports it.
- The backend mounts the Docker socket to orchestrate labs. Treat the host and
  the `docker` group as privileged, keep the backend bound to localhost, and
  expose only the frontend ports required by the deployment.

### Data deletion process

- **Self-service:** Profile → **Privacy and data** → **Delete my account**.
  The request requires the current password, a live TOTP or recovery code when
  MFA is enabled, and typing `DELETE`.
- **Administrator:** Admin → Users → Delete requires typing the username and
  uses the same erasure service.
- Deletion removes identity and credential data, the WireGuard peer and keys,
  enrolments, completions, flag and quiz attempts, achievements, competition
  entries, lab sessions/containers, and WebSocket tickets. Activity and audit
  records are anonymised; authored labs keep their content but lose the author
  link.
- An instructor who owns courses must transfer them first. The last usable
  administrator cannot delete their own account.
- A keyed suppression ledger stores HMAC hashes of the erased username and
  email on the persistent `/workbook` volume. Restores re-apply it so deleted
  accounts cannot be resurrected.
- Backups taken before deletion may retain the account until they age out of
  the 30-day retention window. Activity/audit retention defaults to 90 days.
  Downloaded certificate and transcript PDFs cannot be revoked by the platform.

## Quick Start

Run the setup script on a fresh Ubuntu 22.04+ server (see [Requirements](#requirements) for sizing):

```bash
git clone https://github.com/RobChaykoski/opencyberrange.git
cd opencyberrange
sudo bash scripts/setup-range-server.sh --install
```

Prefer to run Docker Compose yourself? See the
[Docker Compose Deployment Manual](Manual-Lite/00_Server_Deployment/08_Docker_Deploy_Manual.md)
for a command-by-command deployment.

The first prompt in the setup script asks how students will reach the server:

```
How will students access this server?

  1) Local network only
     Students are on the same network as this server
     (classroom, school lab, school network)
     VPN is installed for user isolation; HTTPS uses a self-signed certificate

  2) Over the internet / cloud
     Students connect remotely from home or other locations
     Includes cloud servers (AWS, Azure, Hetzner, OVH, etc.)
     VPN is installed; optional WSTunnel for Cloudflare deployments
```

Both paths install WireGuard VPN for user isolation. The difference is the VPN endpoint address and TLS configuration.

The scenario is not the only prompt. Later in the run the script pauses to ask whether to discover labs into the database (default yes) and whether to pre-build lab images now (default no, since it can take a long time). The internet path adds a WSTunnel prompt and asks for the public IP if it cannot auto-detect one. Every prompt has a sensible default, so pressing Enter accepts it.

### Local Network (Option 1)

Choose option 1 when the server and all student machines are on the same physical network; a classroom, a school lab, or a home setup. The VPN endpoint uses the server's LAN IP, and a self-signed TLS certificate is generated so students connect over HTTPS.

After installation, students open `https://<server-ip>` in a browser, accept the certificate warning once, create an account, download their VPN config, connect with WireGuard, and start working.

### Internet / Cloud (Option 2)

Choose option 2 when students connect from home or other external networks, or when deploying to a cloud server (AWS, Azure, Hetzner, OVH, DigitalOcean, etc.). The VPN endpoint uses the server's public IP. Students download a VPN config from the platform, connect with WireGuard, and access labs over the encrypted tunnel.

A cloud install has not been verified end to end yet, so expect to adjust firewall rules and the VPN endpoint to suit your provider.

#### Cloud provider requirements

If deploying to a cloud provider, open the following ports in your provider's security group or firewall **before** running the setup script:

| Port | Protocol | Purpose |
|------|----------|---------|
| **443** | TCP | Platform web interface (HTTPS) |
| **51820** | UDP | WireGuard VPN tunnel |
| **5555** | TCP | WSTunnel fallback (only if using Cloudflare Tunnel) |

The setup script configures `iptables` on the server itself, but cloud providers add a separate firewall layer that defaults to blocking all inbound traffic. Both layers must allow these ports.

> **Do not open port 5000.** The Peer Manager API is an internal service used by the backend container. It is not meant to be reachable from the internet, and opening it adds attack surface without enabling any student feature.

> **KVM note:** Labs that use QEMU/KVM virtual machines require hardware virtualization. Most standard cloud VPS instances do not expose `/dev/kvm`. Use a bare-metal server (Hetzner AX-series, AWS `.metal` instances, OVH dedicated) or a VPS with nested virtualization enabled. Docker-only labs work on any VPS.

For public-facing deployments behind a domain, the [Cloud Deployment guide](Manual-Lite/00_Server_Deployment/03_Cloud_Deployment.md) covers optional Cloudflare Tunnel configuration.

## What the Setup Script Does

| Phase | Local Network | Internet / Cloud |
|-------|--------------|-------------------|
| 1. System packages | Docker, Python 3, WireGuard, iptables-persistent | Same |
| 2. IP forwarding | Enabled | Enabled |
| 3. WireGuard VPN | Server keys generated, wg0 interface configured (LAN endpoint) | Same (public IP endpoint) |
| 4. Peer Manager API | Deployed internally on port 5000 (never public) | Same |
| 5. VPN firewall rules | NAT, forwarding, and isolation rules applied | Same |
| 6. Host firewall | Ports 80, 443, 51820/UDP opened | Same |
| 7. Platform | `.env` generated, Docker Compose starts backend + frontend + database | Same |
| 7b. Curriculum | Tracks, levels, and all included exercises seeded | Same |
| 7c. WSTunnel | Skipped | Optional; for Cloudflare Tunnel deployments |
| 7d. HTTPS certificate | Self-signed cert generated, frontend rebuilt with HTTPS | Skipped (Cloudflare handles TLS) |
| 8. Verification | Core + VPN + HTTPS checks | Core + VPN + Peer Manager checks |

## Manual Setup

For production deployments or custom configurations, see the [Server Deployment guides](Manual-Lite/00_Server_Deployment/) which cover each step individually. For a direct, command-by-command path, use the [Docker Compose Deployment Manual](Manual-Lite/00_Server_Deployment/08_Docker_Deploy_Manual.md).

## Platform Components

| Component | Technology | Container |
|-----------|-----------|-----------|
| Frontend | Vue.js 3 + Vite, served by nginx | `ocr-frontend` (port 80/443) |
| Backend | Python / FastAPI | `ocr-backend` (port 8000, localhost only) |
| Database | PostgreSQL 15 | `ocr-db` (port 5432, internal only) |
| VPN | WireGuard + Peer Manager API | Host systemd services (port 51820/UDP) |

## Repository Structure

```
opencyberrange/
├── platform/
│   ├── backend/          # FastAPI application, migrations, curriculum/lab scripts
│   ├── frontend/         # Vue.js SPA, nginx config, baked workbook wiki
│   ├── labs/             # Exercise library (organized by track)
│   └── .env.example      # Environment variable template
├── Workbook/             # Student walkthroughs (MkDocs wiki source)
├── Manual-Lite/          # Platform documentation (deployment, student, instructor, admin)
├── tools/                # Wiki generation and maintenance tools
├── .opencode/            # Project-local design and authoring skills
├── scripts/              # Setup, deployment, and lab validation tools
├── BUILD_NOTICE.md       # Updated-build provenance, attribution, and AI disclosure
├── THIRD_PARTY_NOTICES.md # Open-source licence inventory and attribution checklist
├── THIRD_PARTY_LICENSES/  # Notice-sensitive licence texts
└── CONTRIBUTING.md       # Contributor guidelines
```

## Documentation

| Guide | Audience |
|-------|----------|
| [Server Deployment](Manual-Lite/00_Server_Deployment/) | Server administrators deploying the platform |
| [Upgrade and Verify](Manual-Lite/00_Server_Deployment/07_Upgrade_And_Verify.md) | Administrators backing up and upgrading a server, labs, and RangeBox images |
| [Student Guide](Manual-Lite/02_Student_Guide/01_Student_Dashboard.md) | Students using exercises, courses, profiles, and certificates |
| [Migrating Users](Manual-Lite/04_Admin_Guide/26_Migrating_Users.md) | Admins moving accounts from an earlier installation |
| [Workbook](Workbook/index.md) | Students following step-by-step lab walkthroughs |
| [AI Hacking Workbook](Workbook/CH_AI01_AI_Foundations/00_Introduction.md) | Students starting the AI Hacking stream |
| [Architecture](Manual-Lite/00_Server_Deployment/06_Architecture.md) | Developers and operators extending the platform |
| [Build Notice](BUILD_NOTICE.md) | Upstream attribution, AI-assistance disclosure, and changes in this updated build |
| [Third-Party Notices](THIRD_PARTY_NOTICES.md) | Open-source dependencies, licence families, and attribution checklist |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributors submitting labs or platform changes |

## HTTPS

The frontend auto-detects certificates in `platform/certs/` at container startup. When certificates are present, nginx serves HTTPS on port 443 and redirects HTTP to HTTPS. When no certificates are found, nginx serves HTTP only; suitable for Cloudflare Tunnel deployments where TLS terminates at the edge.

To generate a certificate manually (outside the setup script):

```bash
sudo bash scripts/generate-self-signed-cert.sh
cd platform && docker compose up -d frontend
```

## Verifying Health

After installation, log in as admin and navigate to **Admin Panel > System Health**. The health check verifies Docker, the database, disk space, and the Peer Manager VPN service (if installed). All indicators should show green.

## Requirements

- **OS:** Ubuntu 22.04 LTS or later (Debian-based)
- **CPU:** 4+ cores (KVM-capable for shared VM labs)
- **Platform stack:** Python 3.11, Node 22 (frontend build), PostgreSQL 15, Docker Compose v2. Current pins and the upgrade trail are in [`versions.yaml`](https://github.com/RobChaykoski/opencyberrange/blob/main/versions.yaml) and the `WAVE-*.md` documents in `docs/`.
- **RAM:** 32 GB minimum, 64 GB recommended for 20+ concurrent students. Most RAM goes to RangeBoxes (the in-browser desktops), each hard-capped at 2 GB; the platform auto-sizes how many it will start from free memory, keeping an 8 GB reserve. See [Prerequisites and Sizing](Manual-Lite/00_Server_Deployment/01_Prerequisites.md#memory-and-rangebox-capacity).
- **Disk (production):** 500 GB; pre-building all exercise containers uses ~200 GB of images and cache; exercises then start in seconds for students
- **Disk (evaluation):** 100 GB; skip pre-building and let containers build on first launch; the first student to start each exercise waits 1-3 minutes while Docker builds the image, but disk stays small until exercises are actually used
- **Network (local):** Server reachable on the classroom/school network
- **Network (internet/cloud):** Public IP or Cloudflare Tunnel; ports 443/TCP, 51820/UDP, and 5555/TCP (WSTunnel) open in provider firewall
