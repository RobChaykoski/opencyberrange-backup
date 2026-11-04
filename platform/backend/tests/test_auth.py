"""Login smoke tests: bad credentials rejected, JWT issued on good ones."""
import pytest

import jwt

from app.config import settings

pytestmark = pytest.mark.db


def test_login_rejects_wrong_password(client, test_user):
    resp = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "definitely-wrong-pw"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect username or password"


def test_login_rejects_unknown_user(client, db_schema):
    resp = client.post(
        "/api/auth/login",
        data={"username": "pytest_no_such_user", "password": "whatever123"},
    )
    assert resp.status_code == 401
    # Same generic message as a wrong password, so usernames cannot be
    # enumerated from the login endpoint.
    assert resp.json()["detail"] == "Incorrect username or password"


def test_login_issues_jwt_on_good_creds(client, test_user, test_password):
    resp = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": test_password},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == test_user.username
    assert body["user"]["is_approved"] is True

    # The token must be a real JWT signed with the configured secret and
    # carry the username as its subject.
    claims = jwt.decode(
        body["access_token"], settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert claims["sub"] == test_user.username
    assert "exp" in claims


def test_token_grants_access_to_me_endpoint(client, auth_headers, test_user):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == test_user.username


def test_login_and_me_expose_user_timezone(client, db_session, test_user, test_password):
    test_user.timezone = "America/New_York"
    db_session.commit()

    login = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": test_password},
    )
    assert login.status_code == 200, login.text
    assert login.json()["user"]["timezone"] == "America/New_York"

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["timezone"] == "America/New_York"


def test_legacy_bcrypt_hash_is_upgraded_on_login(client, db_session, test_user, test_password):
    """Accounts created before the Argon2 migration keep working and rehash."""
    import bcrypt

    legacy = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt()).decode()
    test_user.hashed_password = legacy
    db_session.commit()

    resp = client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": test_password},
    )
    assert resp.status_code == 200, resp.text

    db_session.refresh(test_user)
    assert test_user.hashed_password.startswith("$argon2"), test_user.hashed_password
