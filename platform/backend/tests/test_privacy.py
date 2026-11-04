"""Privacy tests for IP redaction in user-facing responses.

Private, loopback, link-local, and malformed addresses must not appear in the
account export or session views. Public addresses remain because they are the
account holder's own data.
"""
import json
import uuid

import pytest

from app.models import ActivityEvent, WireGuardConfig
from app.services.privacy import redact_ip

pytestmark = pytest.mark.db


def test_redact_ip_helper():
    assert redact_ip(None) is None
    assert redact_ip("") == ""
    assert redact_ip("10.20.30.40") == "redacted"
    assert redact_ip("172.16.5.9") == "redacted"
    assert redact_ip("192.168.1.10") == "redacted"
    assert redact_ip("127.0.0.1") == "redacted"
    assert redact_ip("169.254.1.1") == "redacted"
    assert redact_ip("::1") == "redacted"
    assert redact_ip("fd00::1") == "redacted"
    assert redact_ip("not-an-ip") == "redacted"
    assert redact_ip("8.8.8.8") == "8.8.8.8"
    assert redact_ip("2001:4860:4860::8888") == "2001:4860:4860::8888"


def test_settings_and_sessions_redact_private_last_login_ip(
    client, auth_headers, test_user, db_session
):
    test_user.last_login_ip = "10.20.30.40"
    db_session.commit()

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200, settings.text
    assert settings.json()["last_login_ip"] == "redacted"

    sessions = client.get("/api/auth/sessions", headers=auth_headers)
    assert sessions.status_code == 200, sessions.text
    assert sessions.json()["current"]["last_login_ip"] == "redacted"


def test_settings_keeps_public_last_login_ip(
    client, auth_headers, test_user, db_session
):
    test_user.last_login_ip = "8.8.8.8"
    db_session.commit()

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200, settings.text
    assert settings.json()["last_login_ip"] == "8.8.8.8"


def test_export_redacts_private_infrastructure_addresses(
    client, auth_headers, test_user, db_session
):
    test_user.last_login_ip = "10.20.30.40"
    db_session.add(WireGuardConfig(
        user_id=test_user.id,
        private_key="test-only-encrypted-key",
        public_key="test-only-public-key",
        client_ip=f"10.{uuid.uuid4().int % 200 + 20}.0.5",
    ))
    db_session.add_all([
        ActivityEvent(
            event_type="login",
            actor_id=test_user.id,
            ip_address="192.168.50.10",
        ),
        ActivityEvent(
            event_type="login",
            actor_id=test_user.id,
            ip_address="8.8.8.8",
        ),
    ])
    db_session.commit()

    try:
        resp = client.get("/api/auth/export", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["account"]["last_login_ip"] == "redacted"
        assert data["vpn"]["client_ip"] == "redacted"
        activity_ips = {event["ip_address"] for event in data["activity"]}
        assert "redacted" in activity_ips
        assert "8.8.8.8" in activity_ips

        serialized = json.dumps(data)
        assert "10.20.30.40" not in serialized
        assert "192.168.50.10" not in serialized
    finally:
        db_session.query(ActivityEvent).filter(
            ActivityEvent.actor_id == test_user.id
        ).delete()
        db_session.query(WireGuardConfig).filter(
            WireGuardConfig.user_id == test_user.id
        ).delete()
        db_session.commit()
