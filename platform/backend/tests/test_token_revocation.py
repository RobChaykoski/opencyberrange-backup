"""Password changes and admin resets must invalidate outstanding tokens."""
import time
import uuid

import pytest

from app.auth import get_password_hash
from app.models import RevokedToken, User

pytestmark = pytest.mark.db

NEW_PASSWORD = "Rotated#Horse9Battery"


def _login(client, username, password):
    return client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )


def _assert_token_dead(client, headers):
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 401


def test_change_password_revokes_existing_tokens(client, auth_headers, test_user):
    # JWT iat has one-second resolution; wait so the token predates the
    # revocation sentinel unambiguously.
    time.sleep(1.1)

    resp = client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "Correct#Horse7Battery",
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json().get("reauth_required") is True

    _assert_token_dead(client, auth_headers)

    # The new password still works, and the token it issues is not caught by
    # the mass-revocation sentinel.
    time.sleep(1.1)
    relogin = _login(client, test_user.username, NEW_PASSWORD)
    assert relogin.status_code == 200, relogin.text
    fresh_headers = {"Authorization": f"Bearer {relogin.json()['access_token']}"}
    assert client.get("/api/auth/me", headers=fresh_headers).status_code == 200


def test_revoke_all_sessions_endpoint(client, auth_headers, db_session, test_user):
    time.sleep(1.1)

    resp = client.post("/api/auth/sessions/revoke-all", headers=auth_headers)
    assert resp.status_code == 200, resp.text

    _assert_token_dead(client, auth_headers)

    rows = (
        db_session.query(RevokedToken)
        .filter(RevokedToken.jti == f"revoke-all:{test_user.username}")
        .count()
    )
    assert rows == 1


def test_admin_password_reset_revokes_target_tokens(client, db_session, test_user, test_password):
    suffix = uuid.uuid4().hex[:10]
    admin = User(
        username=f"pytest_admin_{suffix}",
        email=f"pytest_admin_{suffix}@university.edu",
        hashed_password=get_password_hash("Admin#Horse7Battery"),
        is_active=True,
        is_admin=True,
        role="admin",
        is_approved=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    try:
        student_login = _login(client, test_user.username, test_password)
        assert student_login.status_code == 200, student_login.text
        student_headers = {
            "Authorization": f"Bearer {student_login.json()['access_token']}"
        }

        admin_login = _login(client, admin.username, "Admin#Horse7Battery")
        assert admin_login.status_code == 200, admin_login.text
        admin_headers = {
            "Authorization": f"Bearer {admin_login.json()['access_token']}"
        }

        time.sleep(1.1)
        resp = client.post(
            f"/api/admin/users/{test_user.id}/reset-password",
            headers=admin_headers,
            json={"new_password": NEW_PASSWORD},
        )
        assert resp.status_code == 200, resp.text

        _assert_token_dead(client, student_headers)
    finally:
        db_session.query(RevokedToken).filter(
            RevokedToken.user_id.in_([admin.id, test_user.id])
        ).delete(synchronize_session=False)
        db_session.query(User).filter(User.id == admin.id).delete()
        db_session.commit()
