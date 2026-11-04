"""Survey consent and the survey privacy statement.

The statement is versioned in one place so the text a person agrees to, the
version recorded on their account, and the version stored in the consent
history cannot drift apart. The content follows the PIPEDA principles most
relevant to an optional platform feedback survey: identify the purpose, obtain
meaningful consent, collect only what is needed, limit use and retention, keep
the data safe, and make access, correction, and withdrawal easy.
"""

SURVEY_CONSENT_VERSION = "2026-11-04"
SURVEY_CONSENT_UPDATED = "2026-11-04"


def survey_privacy_statement(contact_email: str) -> dict:
    """Return the current statement as structured sections for the UI."""
    contact = (contact_email or "privacy@opencyberrange.local").strip()
    return {
        "version": SURVEY_CONSENT_VERSION,
        "updated": SURVEY_CONSENT_UPDATED,
        "title": "Survey privacy statement",
        "summary": (
            "Surveys are optional. They ask about the platform and how it is "
            "used so we can improve it. You can opt in, decline, or withdraw "
            "at any time without affecting your access, grades, or support."
        ),
        "contact_email": contact,
        "sections": [
            {
                "heading": "Why we are asking",
                "paragraphs": [
                    "We would like to run occasional short surveys about the "
                    "OpenCyberRange platform: which features people use, what "
                    "is confusing, what is missing, and how the platform "
                    "performs in real classes.",
                    "The surveys are about the platform and its usage only. "
                    "They are not about your personal life, beliefs, health, "
                    "finances, or other sensitive topics.",
                ],
            },
            {
                "heading": "What we collect",
                "paragraphs": [
                    "If you opt in, a survey may ask for your answers about "
                    "features, usability, reliability, and how you use the "
                    "platform. A survey may also record basic context such as "
                    "your role (student or instructor), the track you were "
                    "working in, your browser or device type, and when you "
                    "responded.",
                ],
                "bullets": [
                    "We do not collect your password or password hash.",
                    "We do not collect lab flags, flag attempts, quiz answers, "
                    "or grades through surveys.",
                    "We do not ask for government identifiers, financial "
                    "information, health information, or other sensitive data.",
                    "You can skip any survey question and still submit the rest.",
                ],
            },
            {
                "heading": "Your choice",
                "paragraphs": [
                    "Opting in is voluntary and is not a condition of using the "
                    "platform. Declining or withdrawing has no effect on your "
                    "access, grades, certificates, course enrolment, or support.",
                    "Consent is explicit: you choose to opt in after reading "
                    "this statement. You can withdraw at any time from "
                    "Profile \u2192 Surveys, and the withdrawal takes effect "
                    "immediately for future surveys.",
                ],
            },
            {
                "heading": "How we use and disclose responses",
                "paragraphs": [
                    "Responses are used to improve the platform, prioritise "
                    "fixes, and report aggregate trends to the operator and "
                    "authorised administrators. Results are reported in "
                    "aggregate wherever possible.",
                    "We do not sell survey responses, use them for advertising, "
                    "or disclose them to third parties except to service "
                    "providers bound by confidentiality, or where required by "
                    "law. We do not use survey responses to make automated "
                    "decisions about you.",
                ],
            },
            {
                "heading": "How long we keep it",
                "paragraphs": [
                    "Survey responses are kept for up to 24 months from the "
                    "date of the survey, unless the survey itself states a "
                    "shorter period. After that they are deleted or reduced to "
                    "aggregate statistics that cannot identify you.",
                    "The consent record (the fact that you opted in or out, the "
                    "statement version, and the date) is kept while your "
                    "account is active and for up to 24 months after you "
                    "withdraw, so we can demonstrate that consent was handled "
                    "correctly. It is then deleted.",
                ],
            },
            {
                "heading": "How we protect it",
                "paragraphs": [
                    "Survey data is stored on the platform server and is "
                    "available only to authorised administrators who need it. "
                    "Access is protected by the platform's authentication and "
                    "role controls, data is encrypted in transit, and backups "
                    "are protected and rotated on the platform's normal backup "
                    "schedule.",
                ],
            },
            {
                "heading": "Access, correction, and withdrawal",
                "paragraphs": [
                    "You can see your current consent state and withdraw it "
                    "from Profile \u2192 Surveys. You can download a copy of "
                    "your account data from Profile \u2192 Privacy and data, "
                    "which includes your survey consent state and history.",
                    "To ask for a copy of your survey responses, correct them, "
                    "or delete them, contact the privacy contact below. We will "
                    "respond within 30 days, as required by PIPEDA.",
                ],
            },
            {
                "heading": "Accountability and contact",
                "paragraphs": [
                    "The platform operator is responsible for the personal "
                    "information described here. Questions, access requests, "
                    "corrections, withdrawals, and complaints should go to:",
                ],
                "bullets": [contact],
            },
            {
                "heading": "Changes to this statement",
                "paragraphs": [
                    "If we make a material change to how surveys collect or use "
                    "personal information, we will publish a new version and "
                    "ask you to review and consent again. Your recorded consent "
                    "always names the version you agreed to.",
                ],
            },
        ],
        "note": (
            "This statement covers survey participation only. The platform's "
            "general privacy, data export, and account-erasure practices are "
            "described in the Privacy and data panel and the platform privacy "
            "documentation."
        ),
    }
