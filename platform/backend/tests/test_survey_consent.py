"""Survey consent endpoints and privacy-statement contract."""

from app.models import SurveyConsentEvent, User
from app.services.survey_consent import SURVEY_CONSENT_VERSION


def _state(client, headers):
    resp = client.get("/api/auth/survey-consent", headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_survey_consent_defaults_off(client, auth_headers):
    state = _state(client, auth_headers)
    assert state["opt_in"] is False
    assert state["opted_in_at"] is None
    assert state["current_version"] == SURVEY_CONSENT_VERSION
    statement = state["statement"]
    assert statement["version"] == SURVEY_CONSENT_VERSION
    assert statement["title"]
    assert statement["contact_email"]
    assert len(statement["sections"]) >= 6
    headings = {section["heading"] for section in statement["sections"]}
    assert "What we collect" in headings
    assert "How long we keep it" in headings


def test_opt_in_requires_current_statement_version(client, auth_headers, db_session, test_user):
    resp = client.post(
        "/api/auth/survey-consent",
        headers=auth_headers,
        json={"opt_in": True, "policy_version": "1999-01-01"},
    )
    assert resp.status_code == 400
    db_session.expire_all()
    user = db_session.query(User).filter(User.id == test_user.id).one()
    assert user.survey_opt_in is False
    assert (
        db_session.query(SurveyConsentEvent)
        .filter(SurveyConsentEvent.user_id == test_user.id)
        .count()
        == 0
    )


def test_opt_in_records_state_and_history(client, auth_headers, db_session, test_user):
    resp = client.post(
        "/api/auth/survey-consent",
        headers=auth_headers,
        json={"opt_in": True, "policy_version": SURVEY_CONSENT_VERSION},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["opt_in"] is True
    assert body["opted_in_at"]
    assert body["consent_version"] == SURVEY_CONSENT_VERSION

    db_session.expire_all()
    user = db_session.query(User).filter(User.id == test_user.id).one()
    assert user.survey_opt_in is True
    assert user.survey_consent_version == SURVEY_CONSENT_VERSION
    events = (
        db_session.query(SurveyConsentEvent)
        .filter(SurveyConsentEvent.user_id == test_user.id)
        .all()
    )
    assert [event.action for event in events] == ["opt_in"]
    assert events[0].policy_version == SURVEY_CONSENT_VERSION


def test_withdraw_records_history(client, auth_headers, db_session, test_user):
    assert (
        client.post(
            "/api/auth/survey-consent",
            headers=auth_headers,
            json={"opt_in": True, "policy_version": SURVEY_CONSENT_VERSION},
        ).status_code
        == 200
    )
    resp = client.post(
        "/api/auth/survey-consent",
        headers=auth_headers,
        json={"opt_in": False},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["opt_in"] is False
    assert resp.json()["opted_in_at"] is None

    db_session.expire_all()
    events = (
        db_session.query(SurveyConsentEvent)
        .filter(SurveyConsentEvent.user_id == test_user.id)
        .order_by(SurveyConsentEvent.id)
        .all()
    )
    assert [event.action for event in events] == ["opt_in", "opt_out"]


def test_export_includes_survey_consent(client, auth_headers, test_user):
    assert (
        client.post(
            "/api/auth/survey-consent",
            headers=auth_headers,
            json={"opt_in": True, "policy_version": SURVEY_CONSENT_VERSION},
        ).status_code
        == 200
    )
    resp = client.get("/api/auth/export", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    consent = resp.json()["survey_consent"]
    assert consent["opt_in"] is True
    assert consent["consent_version"] == SURVEY_CONSENT_VERSION
    assert len(consent["history"]) == 1
    assert consent["history"][0]["action"] == "opt_in"
