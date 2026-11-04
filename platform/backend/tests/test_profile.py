"""Profile names and certificate recipient tests.

The profile fields are edited through /api/auth/settings and surfaced by
/api/auth/me. Certificates must print the profile name rather than the login
handle, falling back to the username only when no name has been saved.
"""
import uuid
from datetime import datetime, timezone

import pytest

from app.auth import get_password_hash
from app.models import Lab, LabCompletion, Level, Track, User

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"

# 1x1 transparent PNG, valid for the avatar image verifier.
TINY_PNG = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest.fixture()
def admin_auth(client, db_session):
    """An admin login plus a list tests can use to register created user IDs."""
    suffix = uuid.uuid4().hex[:10]
    admin = User(
        username=f"pytest_admin_{suffix}",
        email=f"pytest_admin_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_admin=True,
        role="admin",
        is_approved=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    resp = client.post(
        "/api/auth/login",
        data={"username": admin.username, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    created_ids = []
    yield headers, created_ids

    for user_id in created_ids:
        db_session.query(User).filter(User.id == user_id).delete()
    db_session.query(User).filter(User.id == admin.id).delete()
    db_session.commit()


def test_display_name_prefers_full_name():
    user = User(username="ada", first_name="Ada", last_name="Lovelace")
    assert user.display_name == "Ada Lovelace"


def test_display_name_falls_back_to_username():
    assert User(username="solo").display_name == "solo"
    assert User(username="solo", first_name="   ", last_name="").display_name == "solo"


def test_display_name_accepts_one_name_part():
    assert User(username="solo", first_name="Grace").display_name == "Grace"
    assert User(username="solo", last_name="Hopper").display_name == "Hopper"


def test_scoreboard_name_modes():
    user = User(username="ada", first_name="Ada", last_name="Lovelace")

    user.scoreboard_name_mode = "real_name"
    assert user.scoreboard_name == "Ada Lovelace"

    user.scoreboard_name_mode = "username"
    assert user.scoreboard_name == "ada"

    user.scoreboard_name_mode = "anonymous"
    assert user.scoreboard_name == "Anonymous participant"

    # Legacy rows created before the preference existed fall back to the name.
    user.scoreboard_name_mode = None
    assert user.scoreboard_name == "Ada Lovelace"


def test_scoreboard_name_mode_round_trip(client, auth_headers, test_user):
    resp = client.put(
        "/api/auth/settings",
        json={"scoreboard_name_mode": "anonymous"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200
    assert settings.json()["scoreboard_name_mode"] == "anonymous"

    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["scoreboard_name_mode"] == "anonymous"


def test_scoreboard_name_mode_rejects_unknown_values(client, auth_headers, test_user):
    resp = client.put(
        "/api/auth/settings",
        json={"scoreboard_name_mode": "stage_name"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_profile_names_are_saved_and_returned(client, auth_headers, test_user):
    resp = client.put(
        "/api/auth/settings",
        json={"first_name": "Grace", "last_name": "Hopper"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["first_name"] == "Grace"
    assert me.json()["last_name"] == "Hopper"

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200
    assert settings.json()["first_name"] == "Grace"
    assert settings.json()["last_name"] == "Hopper"


def test_profile_names_can_be_cleared(client, auth_headers, test_user):
    client.put(
        "/api/auth/settings",
        json={"first_name": "Grace", "last_name": "Hopper"},
        headers=auth_headers,
    )
    resp = client.put(
        "/api/auth/settings",
        json={"first_name": "", "last_name": ""},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert not me.json()["first_name"]
    assert not me.json()["last_name"]


def test_profile_avatar_round_trip(client, auth_headers, test_user):
    resp = client.put(
        "/api/auth/settings",
        json={"avatar_data": TINY_PNG},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["avatar_data"] == TINY_PNG

    settings = client.get("/api/auth/settings", headers=auth_headers)
    assert settings.status_code == 200
    assert settings.json()["avatar_data"] == TINY_PNG

    summary = client.get("/api/profile/summary", headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json()["user"]["avatar_data"] == TINY_PNG

    cleared = client.put(
        "/api/auth/settings",
        json={"avatar_data": ""},
        headers=auth_headers,
    )
    assert cleared.status_code == 200, cleared.text
    assert client.get("/api/auth/me", headers=auth_headers).json()["avatar_data"] is None


def test_profile_avatar_rejects_non_image_data(client, auth_headers, test_user):
    resp = client.put(
        "/api/auth/settings",
        json={"avatar_data": "data:image/svg+xml;base64,PHN2Zz48L3N2Zz4="},
        headers=auth_headers,
    )
    assert resp.status_code == 422

    not_base64 = client.put(
        "/api/auth/settings",
        json={"avatar_data": "data:image/png;base64,not really an image"},
        headers=auth_headers,
    )
    assert not_base64.status_code == 422


def test_profile_summary_includes_certificates_and_completions(
    client, auth_headers, test_user, completed_level
):
    track, level = completed_level
    resp = client.get("/api/profile/summary", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    matching = [c for c in body["certificates"] if c["track_slug"] == track.slug]
    assert len(matching) == 1
    certificate = matching[0]
    assert certificate["level_id"] == level.id
    assert certificate["recipient"] == test_user.display_name
    assert certificate["exercises_completed"] == 1
    assert certificate["exercises_total"] == 1

    completion = next(
        item for item in body["completions"] if item["lab_slug"].startswith("certificate-lab-")
    )
    assert completion["track_slug"] == track.slug
    assert completion["completed_at"]


def test_profile_transcript_pdf(client, auth_headers, completed_level):
    resp = client.get("/api/profile/transcript.pdf", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/pdf")
    assert "attachment" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF")


@pytest.fixture()
def completed_level(db_session, test_user):
    """A public one-lab level that test_user has completed."""
    suffix = uuid.uuid4().hex[:10]
    track = Track(
        name=f"Certificate Test {suffix}",
        slug=f"certificate-test-{suffix}",
        is_active=True,
    )
    db_session.add(track)
    db_session.flush()

    level = Level(
        track_id=track.id,
        level_number=1,
        name="Certificate Level",
    )
    db_session.add(level)
    db_session.flush()

    lab = Lab(
        name=f"Certificate Lab {suffix}",
        slug=f"certificate-lab-{suffix}",
        description="Created by the automated test harness",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        level_id=level.id,
    )
    db_session.add(lab)
    db_session.flush()

    completion = LabCompletion(
        user_id=test_user.id,
        lab_id=lab.id,
        flag_submitted="OCR{test_flag}",
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(completion)
    db_session.commit()

    yield track, level

    db_session.query(LabCompletion).filter(LabCompletion.lab_id == lab.id).delete()
    db_session.query(Lab).filter(Lab.id == lab.id).delete()
    db_session.query(Level).filter(Level.id == level.id).delete()
    db_session.query(Track).filter(Track.id == track.id).delete()
    db_session.commit()


def test_certificate_uses_profile_name(
    client, auth_headers, test_user, completed_level
):
    track, level = completed_level
    client.put(
        "/api/auth/settings",
        json={"first_name": "Grace", "last_name": "Hopper"},
        headers=auth_headers,
    )

    resp = client.get(
        f"/api/exercises/tracks/{track.slug}/levels/{level.id}/certificate",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["recipient"] == "Grace Hopper"


def test_certificate_falls_back_to_username(
    client, auth_headers, test_user, completed_level
):
    track, level = completed_level

    resp = client.get(
        f"/api/exercises/tracks/{track.slug}/levels/{level.id}/certificate",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["recipient"] == test_user.username


def test_admin_can_create_user_with_names(client, admin_auth):
    headers, created_ids = admin_auth
    suffix = uuid.uuid4().hex[:10]
    resp = client.post(
        "/api/admin/users/create",
        json={
            "username": f"pytest_named_{suffix}",
            "email": f"pytest_named_{suffix}@university.edu",
            "password": TEST_PASSWORD,
            "first_name": "Ada",
            "last_name": "Lovelace",
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    created_ids.append(body["id"])
    assert body["first_name"] == "Ada"
    assert body["last_name"] == "Lovelace"


def test_admin_can_edit_user_names(client, admin_auth):
    headers, created_ids = admin_auth
    suffix = uuid.uuid4().hex[:10]
    created = client.post(
        "/api/admin/users/create",
        json={
            "username": f"pytest_edit_{suffix}",
            "email": f"pytest_edit_{suffix}@university.edu",
            "password": TEST_PASSWORD,
        },
        headers=headers,
    )
    assert created.status_code == 200, created.text
    user_id = created.json()["id"]
    created_ids.append(user_id)

    resp = client.put(
        f"/api/admin/users/{user_id}",
        json={"first_name": "Grace", "last_name": "Hopper"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["first_name"] == "Grace"
    assert resp.json()["last_name"] == "Hopper"

    cleared = client.put(
        f"/api/admin/users/{user_id}",
        json={"first_name": "", "last_name": ""},
        headers=headers,
    )
    assert cleared.status_code == 200, cleared.text
    assert not cleared.json()["first_name"]
    assert not cleared.json()["last_name"]
