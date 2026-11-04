"""Account erasure for the GDPR right to erasure.

This module owns the destructive part of account deletion so the admin path and
the self-service path cannot drift apart. It erases the account row and
user-owned rows, anonymises security/audit records, and removes external state
(WireGuard peer and lab containers).

Design rules:
- Never delete a course owned by the user: courses belong to other students too.
  Deletion is blocked until an admin transfers them (Admin -> Courses -> Manage).
- Never delete the last usable administrator.
- Commit the database transaction first, then do best-effort external cleanup.
  A failed Docker/WireGuard call must not leave the account half-erased.
- Do not put usernames or email addresses in new logs.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.services.erasure_ledger import append_erasure

from app.models import (
    Achievement,
    ActivityEvent,
    Competition,
    CompetitionParticipant,
    Course,
    CourseCompletionReset,
    CourseEnrollment,
    ExerciseGenJob,
    ExerciseTemplate,
    ExerciseTestResult,
    FlagAttempt,
    InstructorApiKey,
    InviteCode,
    Lab,
    LabCompletion,
    LabSession,
    QuizAttempt,
    RevokedToken,
    StudioPendingReview,
    SurveyConsentEvent,
    TemplateInstance,
    User,
    WireGuardConfig,
)

logger = logging.getLogger(__name__)


class ErasureBlocked(Exception):
    """Deletion cannot proceed without an operator decision.

    ``code`` is a stable machine-readable value for the frontend:
    ``last_admin``, ``owned_courses``, or ``constraint``.
    """

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


@dataclass
class ErasureResult:
    user_id: int
    deleted: dict[str, int] = field(default_factory=dict)
    anonymised: dict[str, int] = field(default_factory=dict)
    external: dict[str, list[str]] = field(default_factory=dict)
    ledger: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "deleted": self.deleted,
            "anonymised": self.anonymised,
            "external": self.external,
            "ledger": self.ledger,
        }


# Optional tables that exist only on some editions. Names are fixed constants,
# never request input. ``delete`` removes rows owned by the user; ``null``
# keeps the record and drops only the identity link.
_OPTIONAL_USER_REFERENCES: tuple[tuple[str, str, str], ...] = (
    ("ws_tickets", "user_id", "delete"),
    ("llmr_seats", "user_id", "delete"),
    ("llmr_findings", "user_id", "delete"),
    ("llmr_defense_configs", "submitted_by", "null"),
    ("soc_exercise_attempts", "user_id", "delete"),
    ("soc_exercise_flags", "user_id", "delete"),
)


def _table_exists(db: Session, table: str) -> bool:
    return bool(
        db.execute(text("SELECT to_regclass(:table)"), {"table": table}).scalar()
    )


def _apply_optional_references(db: Session, user_id: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table, column, action in _OPTIONAL_USER_REFERENCES:
        if not _table_exists(db, table):
            continue
        try:
            if action == "delete":
                stmt = text(f"DELETE FROM {table} WHERE {column} = :uid")
            else:
                stmt = text(f"UPDATE {table} SET {column} = NULL WHERE {column} = :uid")
            result = db.execute(stmt, {"uid": user_id})
            if result.rowcount:
                counts[table] = result.rowcount
        except Exception as exc:  # pragma: no cover - edition/table drift
            logger.warning("Erasure cleanup skipped %s.%s: %s", table, column, exc)
    return counts


def _ensure_deletable(db: Session, user: User) -> None:
    """Raise ErasureBlocked when deletion would harm the platform or others."""
    if user.role == "admin":
        remaining_admins = (
            db.query(User)
            .filter(
                User.id != user.id,
                User.role == "admin",
                User.is_active.is_(True),
                User.is_locked.is_(False),
            )
            .count()
        )
        if remaining_admins == 0:
            raise ErasureBlocked(
                "last_admin",
                "This is the last usable administrator account. "
                "Create or promote another administrator before deleting this one.",
            )

    owned_courses = (
        db.query(Course)
        .filter(Course.instructor_id == user.id)
        .order_by(Course.code)
        .all()
    )
    if owned_courses:
        raise ErasureBlocked(
            "owned_courses",
            "This account owns courses. Transfer each course to another instructor "
            "first; deleting the account would also delete every enrolled student's "
            "course records.",
            {
                "courses": [
                    {"id": c.id, "code": c.code, "name": c.name}
                    for c in owned_courses
                ]
            },
        )


def _delete_where(db: Session, model, column, user_id: int) -> int:
    return (
        db.query(model)
        .filter(column == user_id)
        .delete(synchronize_session=False)
    )


def _null_where(db: Session, model, column, user_id: int) -> int:
    return (
        db.query(model)
        .filter(column == user_id)
        .update({column: None}, synchronize_session=False)
    )


def _anonymise_activity(db: Session, user_id: int, username: str) -> dict[str, int]:
    """Keep the security record, remove the identity.

    Events targeting the user lose target_id/target_label/detail. Events the
    user performed keep their action and timestamp but lose actor_id and IP.
    """
    counts: dict[str, int] = {}

    counts["activity_target"] = (
        db.query(ActivityEvent)
        .filter(
            ActivityEvent.target_type == "user",
            ActivityEvent.target_id == user_id,
        )
        .update(
            {
                ActivityEvent.target_id: None,
                ActivityEvent.target_label: None,
                ActivityEvent.detail: None,
            },
            synchronize_session=False,
        )
    )
    counts["activity_actor"] = (
        db.query(ActivityEvent)
        .filter(ActivityEvent.actor_id == user_id)
        .update(
            {
                ActivityEvent.actor_id: None,
                ActivityEvent.ip_address: None,
            },
            synchronize_session=False,
        )
    )
    # Defensive: some events store the username in target_label without using
    # target_type='user' (legacy rows and admin actions).
    if username:
        counts["activity_label"] = (
            db.query(ActivityEvent)
            .filter(ActivityEvent.target_label == username)
            .update(
                {ActivityEvent.target_label: None, ActivityEvent.detail: None},
                synchronize_session=False,
            )
        )
    return {k: v for k, v in counts.items() if v}


def _external_cleanup(
    user_id: int, lab_slugs: Iterable[str], public_key: str | None
) -> dict[str, list[str]]:
    """Best-effort removal of state that lives outside PostgreSQL."""
    external: dict[str, list[str]] = {
        "labs_destroyed": [],
        "lab_errors": [],
        "wireguard": [],
    }

    # Import lazily: test suites create users without Docker or a WG server.
    try:
        from app.services.docker_manager import DockerManager

        docker = DockerManager()
    except Exception as exc:  # pragma: no cover - environment dependent
        docker = None
        external["lab_errors"].append(f"docker unavailable: {exc}")

    for slug in sorted(set(lab_slugs)):
        if docker is None:
            break
        try:
            docker.destroy_lab_environment(user_id, slug)
            external["labs_destroyed"].append(slug)
        except Exception as exc:  # pragma: no cover - environment dependent
            logger.warning("Erasure could not destroy lab %s for user %s: %s", slug, user_id, exc)
            external["lab_errors"].append(f"{slug}: {exc}")

    if public_key:
        try:
            from app.services.wireguard_manager import WireGuardManager

            if WireGuardManager().remove_peer(public_key):
                external["wireguard"].append("peer removed")
            else:
                external["wireguard"].append("peer removal returned false")
        except Exception as exc:  # pragma: no cover - environment dependent
            logger.warning("Erasure could not remove WireGuard peer for user %s: %s", user_id, exc)
            external["wireguard"].append(f"error: {exc}")

    return external


def erase_user(
    db: Session,
    user: User,
    *,
    actor: str = "self",
    external_cleanup: bool = True,
    write_ledger: bool = True,
) -> ErasureResult:
    """Erase an account and its personal data.

    Raises ErasureBlocked before touching anything when the account owns
    courses or is the last administrator. ``external_cleanup=False`` is for
    tests and maintenance tasks that should not touch Docker or WireGuard.
    ``write_ledger=False`` is only for tests; production erasure must record
    the suppression entry so a restore cannot resurrect the account.
    """
    if user is None or user.id is None:
        raise ValueError("erase_user requires a persisted user")

    _ensure_deletable(db, user)

    user_id = user.id
    username = user.username
    email = (user.email or "").strip()
    result = ErasureResult(user_id=user_id)

    # Record the suppression entry before touching the database. If this cannot
    # be written, abort: a restore from a pre-deletion backup would otherwise
    # bring the account back and silently undo the erasure.
    if write_ledger:
        try:
            result.ledger = append_erasure(username, email, actor=actor)
        except Exception as exc:
            raise ErasureBlocked(
                "ledger_unavailable",
                "Could not record the erasure in the suppression ledger. "
                "Deletion was stopped so a backup restore cannot resurrect the account.",
                {"error": str(exc)},
            ) from exc

    # Capture external state before the rows disappear.
    sessions = (
        db.query(LabSession)
        .options(joinedload(LabSession.lab))
        .filter(LabSession.user_id == user_id)
        .all()
    )
    lab_slugs = [s.lab.slug for s in sessions if s.lab is not None]
    wg_config = db.query(WireGuardConfig).filter(WireGuardConfig.user_id == user_id).first()
    public_key = wg_config.public_key if wg_config else None

    # Template instances owned by the user may be referenced by review rows
    # whose FK has no ON DELETE action.
    instance_ids = [
        row[0]
        for row in db.query(TemplateInstance.id)
        .filter(TemplateInstance.instructor_id == user_id)
        .all()
    ]
    if instance_ids:
        db.query(StudioPendingReview).filter(
            StudioPendingReview.instance_id.in_(instance_ids)
        ).delete(synchronize_session=False)

    # Drop identity links from records that outlive the account.
    db.query(StudioPendingReview).filter(
        StudioPendingReview.reviewed_by == user_id
    ).update({StudioPendingReview.reviewer_notes: None}, synchronize_session=False)

    for model, column in (
        (CourseCompletionReset, CourseCompletionReset.reset_by),
        (LabSession, LabSession.impersonated_by),
        (InviteCode, InviteCode.used_by),
        (ExerciseTestResult, ExerciseTestResult.tested_by_id),
        (StudioPendingReview, StudioPendingReview.reviewed_by),
        (Lab, Lab.created_by),
        (ExerciseTemplate, ExerciseTemplate.created_by),
        (Competition, Competition.created_by),
    ):
        count = _null_where(db, model, column, user_id)
        if count:
            result.anonymised[model.__tablename__] = count

    # Invented invite addresses are personal data even when the code belongs to
    # someone else.
    if email:
        count = (
            db.query(InviteCode)
            .filter(func.lower(InviteCode.email) == email.lower())
            .update({InviteCode.email: None}, synchronize_session=False)
        )
        if count:
            result.anonymised["invite_emails"] = count

    result.anonymised.update(_anonymise_activity(db, user_id, username))

    # Rows that belong to the account. Order matters where a parent row is
    # referenced by another table without a cascade rule.
    for model, column in (
        (CourseCompletionReset, CourseCompletionReset.user_id),
        (Achievement, Achievement.user_id),
        (CourseEnrollment, CourseEnrollment.user_id),
        (FlagAttempt, FlagAttempt.user_id),
        (LabCompletion, LabCompletion.user_id),
        (QuizAttempt, QuizAttempt.user_id),
        (LabSession, LabSession.user_id),
        (CompetitionParticipant, CompetitionParticipant.user_id),
        (RevokedToken, RevokedToken.user_id),
        (SurveyConsentEvent, SurveyConsentEvent.user_id),
        (InstructorApiKey, InstructorApiKey.instructor_id),
        (WireGuardConfig, WireGuardConfig.user_id),
        (StudioPendingReview, StudioPendingReview.instructor_id),
        (ExerciseGenJob, ExerciseGenJob.instructor_id),
        (TemplateInstance, TemplateInstance.instructor_id),
        (InviteCode, InviteCode.created_by),
    ):
        count = _delete_where(db, model, column, user_id)
        if count:
            result.deleted[model.__tablename__] = count

    for table, count in _apply_optional_references(db, user_id).items():
        result.deleted[table] = count

    # The ORM may still hold stale child objects after bulk deletes.
    db.expire_all()
    deleted_user = db.query(User).filter(User.id == user_id).first()
    if deleted_user is not None:
        try:
            db.delete(deleted_user)
            db.commit()
        except Exception as exc:
            db.rollback()
            # The suppression entry was written before the delete. Negate it so
            # a future restore does not purge an account that still exists.
            if write_ledger and result.ledger:
                try:
                    append_erasure(username, email, actor=actor, status="cancelled")
                except Exception:
                    logger.exception(
                        "Could not cancel erasure ledger entry after a failed delete"
                    )
            match = re.search(r'on table "([A-Za-z0-9_]+)"', str(exc))
            table = match.group(1) if match else None
            logger.error("Erasure blocked by a database constraint for user %s: %s", user_id, exc)
            message = (
                f"Records in '{table}' still reference this account."
                if table
                else "A database constraint blocked account deletion."
            )
            raise ErasureBlocked(
                "constraint",
                message,
                {"table": table} if table else {},
            ) from exc
    result.deleted["users"] = 1

    # External cleanup happens after the commit so a failure cannot roll back
    # the erasure or leave the account half-deleted.
    if external_cleanup:
        result.external = _external_cleanup(user_id, lab_slugs, public_key)

    logger.info(
        "Account erased (actor=%s, user_id=%s, ledger=%s, deleted=%s, anonymised=%s)",
        actor,
        user_id,
        result.ledger,
        result.deleted,
        result.anonymised,
    )
    return result
