# Survey privacy and consent

This document describes the optional survey consent feature. It is an
engineering and operations reference, not legal advice. The published
statement is versioned in `platform/backend/app/services/survey_consent.py`;
change that file and the version constant together when the wording changes.

## How consent works

- Survey participation is **off by default**.
- A learner or instructor opens **Profile → Surveys**.
- Clicking **Opt in to surveys** opens the full privacy statement. Consent is
  only recorded after the person reviews the statement and presses
  **I agree — opt me in**.
- The account stores the opt-in flag, the timestamp, and the statement version.
- Every opt-in and withdrawal is appended to `survey_consent_events` with the
  statement version and timestamp.
- Withdrawal is immediate for future surveys and is also recorded.
- Declining or withdrawing has no effect on platform access, grades,
  certificates, enrolments, or support.
- The account data export (`/api/auth/export`) includes the current state and
  the consent history.

## What the statement covers

The published statement follows the PIPEDA principles that matter for an
optional feedback survey:

- **Purpose** — improve the platform and understand how it is used.
- **Scope** — platform features, usability, reliability, and usage only.
- **Minimal collection** — no passwords, grades, lab flags, or sensitive
  personal information.
- **Meaningful consent** — explicit opt-in after the statement is shown;
  withdrawal is easy.
- **Limits on use and disclosure** — no sale, no advertising, aggregate
  reporting, service providers and legal requirements only.
- **Retention** — responses up to 24 months unless a survey states otherwise;
  consent records while the account is active plus up to 24 months after
  withdrawal.
- **Safeguards** — authorised administrator access, encryption in transit, and
  the platform backup schedule.
- **Access and correction** — data export, contact route, 30-day response.
- **Accountability** — a monitored privacy contact address.

## Configuration

Set a monitored role address in the deployment `.env`:

```bash
PRIVACY_CONTACT_EMAIL=privacy@example.org
```

The value is returned in the statement and shown in the UI. Do not use a
personal mailbox that may leave the organisation.

## Operational notes

- The `survey_consent_events` table is append-only from the application's point
  of view. Do not edit it by hand; it is the record that consent was handled
  correctly.
- Account erasure deletes the account row and cascades to the consent events.
- A new statement version is a material change: update
  `SURVEY_CONSENT_VERSION` and `SURVEY_CONSENT_UPDATED`, then ask people to
  review and consent again. Existing opt-ins remain recorded against the
  version they agreed to.
- Survey responses themselves are not stored by the platform yet. If a future
  survey feature stores responses, add that store to this document, to the
  erasure service, and to the account export before collecting responses.
