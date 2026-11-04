"""Celebration wall API tests.

The wall is shared by every signed-in user, so its visibility rules matter:
active users who opted out of scoreboards and diagnostic admin accounts must
not appear in the public feed, stats, or spotlight. A user's own awards are
still returned in the personal corner.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Achievement, Course, CustomAchievement, User

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


@pytest.fixture()
def celebration_data(db_session, test_user):
    """A course with one public earner, one private earner, and an admin."""
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)

    instructor = User(
        username=f"celebration_instructor_{suffix}",
        email=f"celebration_instructor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        role="instructor",
        is_approved=True,
    )
    db_session.add(instructor)
    db_session.flush()

    course = Course(
        name=f"Celebration Test {suffix}",
        code=f"CE{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"CELEB-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=30),
        end_date=now + timedelta(days=30),
        is_active=True,
    )
    db_session.add(course)
    db_session.flush()

    other = User(
        username=f"celebration_other_{suffix}",
        email=f"celebration_other_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        first_name="Ada",
        last_name="Lovelace",
        is_active=True,
        role="student",
        is_approved=True,
        show_on_scoreboard=True,
    )
    hidden = User(
        username=f"celebration_hidden_{suffix}",
        email=f"celebration_hidden_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        first_name="Hidden",
        last_name="Hacker",
        is_active=True,
        role="student",
        is_approved=True,
        show_on_scoreboard=False,
    )
    admin = User(
        username=f"celebration_admin_{suffix}",
        email=f"celebration_admin_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_admin=True,
        role="admin",
        is_approved=True,
        show_on_scoreboard=True,
    )
    db_session.add_all([other, hidden, admin])
    db_session.flush()

    custom = CustomAchievement(
        name=f"Rocket Rider {suffix}",
        description="Reach a custom celebration milestone.",
        icon="\U0001F680",
        trigger="labs_completed",
        threshold=1,
        is_active=True,
    )
    db_session.add(custom)
    db_session.flush()

    db_session.add_all([
        Achievement(
            user_id=test_user.id,
            course_id=course.id,
            achievement_type="first_blood",
            awarded_at=now - timedelta(minutes=5),
        ),
        Achievement(
            user_id=other.id,
            course_id=course.id,
            achievement_type="no_hints",
            awarded_at=now - timedelta(minutes=4),
        ),
        Achievement(
            user_id=other.id,
            course_id=course.id,
            achievement_type=f"custom_{custom.id}",
            awarded_at=now - timedelta(minutes=3),
        ),
        Achievement(
            user_id=hidden.id,
            course_id=course.id,
            achievement_type="clean_sweep",
            awarded_at=now - timedelta(minutes=2),
        ),
        Achievement(
            user_id=admin.id,
            course_id=course.id,
            achievement_type="perfectionist",
            awarded_at=now - timedelta(minutes=1),
        ),
    ])
    db_session.commit()

    yield {
        "course": course,
        "other": other,
        "hidden": hidden,
        "admin": admin,
        "custom": custom,
    }

    db_session.query(Achievement).filter(
        Achievement.course_id == course.id
    ).delete()
    db_session.query(CustomAchievement).filter(
        CustomAchievement.id == custom.id
    ).delete()
    db_session.query(Course).filter(Course.id == course.id).delete()
    for user_id in (instructor.id, other.id, hidden.id, admin.id):
        db_session.query(User).filter(User.id == user_id).delete()
    db_session.commit()


def test_wall_shows_public_earners_and_resolves_badge_details(
    client, auth_headers, celebration_data, test_user
):
    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    recent_user_ids = {item["user_id"] for item in body["recent"]}
    assert test_user.id in recent_user_ids
    assert celebration_data["other"].id in recent_user_ids
    assert celebration_data["hidden"].id not in recent_user_ids
    assert celebration_data["admin"].id not in recent_user_ids

    other_items = [
        item for item in body["recent"]
        if item["user_id"] == celebration_data["other"].id
    ]
    assert other_items
    assert all(item["display_name"] == "Ada Lovelace" for item in other_items)

    first = next(
        item for item in body["recent"]
        if item["user_id"] == test_user.id
        and item["achievement_type"] == "first_blood"
    )
    assert first["label"] == "First Blood"
    assert first["icon"] == "\U0001F3AF"
    assert first["description"]
    assert first["is_mine"] is True

    custom = next(
        item for item in body["recent"]
        if item["achievement_type"].startswith("custom_")
    )
    assert custom["label"] == celebration_data["custom"].name
    assert custom["icon"] == "\U0001F680"
    assert custom["description"] == celebration_data["custom"].description

    spotlight_ids = {row["user_id"] for row in body["spotlight"]}
    assert test_user.id in spotlight_ids
    assert celebration_data["other"].id in spotlight_ids
    assert celebration_data["hidden"].id not in spotlight_ids
    assert celebration_data["admin"].id not in spotlight_ids

    assert body["stats"]["total_awards"] >= 3
    assert body["stats"]["awards_this_week"] >= 3
    assert body["stats"]["first_bloods"] >= 1

    assert body["me"]["badge_count"] == 1
    assert body["me"]["listed"] is True
    assert body["me"]["can_list"] is True
    assert body["me"]["recent"][0]["achievement_type"] == "first_blood"


def test_opted_out_user_keeps_a_private_personal_corner(
    client, auth_headers, celebration_data, test_user
):
    hidden = client.put(
        "/api/auth/settings",
        json={"show_on_scoreboard": False},
        headers=auth_headers,
    )
    assert hidden.status_code == 200, hidden.text

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert test_user.id not in {item["user_id"] for item in body["recent"]}
    assert test_user.id not in {row["user_id"] for row in body["spotlight"]}

    assert body["me"]["listed"] is False
    assert body["me"]["can_list"] is True
    assert body["me"]["badge_count"] == 1
    assert body["me"]["recent"][0]["achievement_type"] == "first_blood"


def test_wall_can_show_the_username(
    client, auth_headers, celebration_data, db_session
):
    other = celebration_data["other"]
    other.scoreboard_name_mode = "username"
    db_session.commit()

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    items = [
        item for item in body["recent"]
        if item["user_id"] == other.id
    ]
    assert items
    assert all(item["display_name"] == other.username for item in items)
    assert all(item["username"] == other.username for item in items)
    assert all(item["name_mode"] == "username" for item in items)


def test_wall_can_show_an_anonymous_name(
    client, auth_headers, celebration_data, db_session
):
    other = celebration_data["other"]
    other.scoreboard_name_mode = "anonymous"
    db_session.commit()

    resp = client.get(
        "/api/dashboard/celebrations?limit=50", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    items = [
        item for item in body["recent"]
        if item["user_id"] == other.id
    ]
    assert items
    assert all(item["display_name"] == "Anonymous participant" for item in items)
    assert all(item["username"] is None for item in items)
    assert all(item["name_mode"] == "anonymous" for item in items)
    assert other.id in {row["user_id"] for row in body["spotlight"]}
