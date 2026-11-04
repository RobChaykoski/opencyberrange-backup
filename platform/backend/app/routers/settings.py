"""
Platform settings API router.
All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.ratelimit import create_limiter

from app.database import get_db
from app.auth import get_current_admin_user
from app.models import User, CustomAchievement
from app.schemas import (
    SettingsBulkUpdate, CustomAchievementCreate, CustomAchievementUpdate,
)
from app.services import settings_service
from app.services.achievements import CUSTOM_ACHIEVEMENT_TRIGGERS
from app.services.audit import log_admin_action, AuditActions

router = APIRouter()
limiter = create_limiter()


def _serialize_custom_achievement(row: CustomAchievement) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "description": row.description or "",
        "icon": row.icon or "\U0001F3C5",
        "trigger": row.trigger,
        "threshold": row.threshold,
        "is_active": row.is_active,
        "created_at": row.created_at,
    }


def _validate_trigger(trigger: str) -> None:
    if trigger not in CUSTOM_ACHIEVEMENT_TRIGGERS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unknown trigger. Choose one of: "
                + ", ".join(sorted(CUSTOM_ACHIEVEMENT_TRIGGERS))
            ),
        )


@router.get(
    "/custom-achievements",
    summary="List custom achievements",
    response_description="Admin-defined achievement definitions",
)
async def list_custom_achievements(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Return every admin-defined achievement, including inactive ones.

    Built-in achievements (first blood, no hints, and so on) are code paths and
    are not listed here. ``trigger`` is one of the keys in
    ``CUSTOM_ACHIEVEMENT_TRIGGERS``; ``threshold`` is the count required for the
    count-based triggers and is ignored by ``course_completed``.
    """
    rows = db.query(CustomAchievement).order_by(
        CustomAchievement.created_at.asc(), CustomAchievement.id.asc()
    ).all()
    return {
        "achievements": [_serialize_custom_achievement(r) for r in rows],
        "triggers": [
            {"value": key, "label": label}
            for key, label in CUSTOM_ACHIEVEMENT_TRIGGERS.items()
        ],
    }


@router.post(
    "/custom-achievements",
    status_code=201,
    summary="Create a custom achievement",
    response_description="The newly created achievement definition",
)
async def create_custom_achievement(
    payload: CustomAchievementCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Create an achievement that is awarded automatically on flag submission.

    The award is evaluated for every course the student is enrolled in, after
    the built-in achievement checks. Existing completions are not re-scored
    retroactively; the definition applies from the next correct flag onward.
    """
    _validate_trigger(payload.trigger)

    row = CustomAchievement(
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
        icon=payload.icon or "\U0001F3C5",
        trigger=payload.trigger,
        threshold=payload.threshold,
        is_active=payload.is_active,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    log_admin_action(
        action=AuditActions.SETTINGS_UPDATED,
        admin_user_id=admin.id,
        admin_username=admin.username,
        target_type="custom_achievement",
        target_id=row.id,
        target_identifier=row.name,
        details={"trigger": row.trigger, "threshold": row.threshold},
        ip_address=request.client.host if request.client else None,
    )
    return _serialize_custom_achievement(row)


@router.put(
    "/custom-achievements/{achievement_id}",
    summary="Update a custom achievement",
    response_description="The updated achievement definition",
)
async def update_custom_achievement(
    achievement_id: int,
    payload: CustomAchievementUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Update a custom achievement. Omitted fields are left unchanged."""
    row = db.query(CustomAchievement).filter(
        CustomAchievement.id == achievement_id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Custom achievement not found")

    if payload.trigger is not None:
        _validate_trigger(payload.trigger)
        row.trigger = payload.trigger
    if payload.name is not None:
        row.name = payload.name.strip()
    if payload.description is not None:
        row.description = payload.description.strip() or None
    if payload.icon is not None:
        row.icon = payload.icon or "\U0001F3C5"
    if payload.threshold is not None:
        row.threshold = payload.threshold
    if payload.is_active is not None:
        row.is_active = payload.is_active

    db.commit()
    db.refresh(row)

    log_admin_action(
        action=AuditActions.SETTINGS_UPDATED,
        admin_user_id=admin.id,
        admin_username=admin.username,
        target_type="custom_achievement",
        target_id=row.id,
        target_identifier=row.name,
        details={"updated": True},
        ip_address=request.client.host if request.client else None,
    )
    return _serialize_custom_achievement(row)


@router.delete(
    "/custom-achievements/{achievement_id}",
    summary="Delete a custom achievement",
    response_description="Deletion confirmation",
)
async def delete_custom_achievement(
    achievement_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Delete a custom achievement definition.

    Awards that students already earned are kept; their label falls back to the
    stored achievement type once the definition is gone.
    """
    row = db.query(CustomAchievement).filter(
        CustomAchievement.id == achievement_id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Custom achievement not found")

    name = row.name
    db.delete(row)
    db.commit()

    log_admin_action(
        action=AuditActions.SETTINGS_UPDATED,
        admin_user_id=admin.id,
        admin_username=admin.username,
        target_type="custom_achievement",
        target_id=achievement_id,
        target_identifier=name,
        details={"deleted": True},
        ip_address=request.client.host if request.client else None,
    )
    return {"message": f"Deleted '{name}'", "id": achievement_id}


@router.get("/")
async def get_all_settings(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Return all platform settings grouped by category. Secret values are masked."""
    return settings_service.get_all_settings(db)


@router.get("/{category}")
async def get_settings_by_category(
    category: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Return settings for a specific category."""
    valid_categories = ["general", "security", "labs", "vpn", "appearance", "modules"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {valid_categories}"
        )
    return settings_service.get_settings_by_category(db, category)


@router.put("/")
# Toggles persist on click, so a normal admin session writes one setting at a
# time instead of batching everything behind one Save. Ten a minute is below
# what flipping a few switches costs and would reject legitimate use. This is an
# authenticated admin-only route; the limit is a runaway guard, not a gate.
@limiter.limit("60/minute")
async def update_settings(
    request: Request,
    payload: SettingsBulkUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Bulk update platform settings."""
    # Filter out masked secret values so admins don't accidentally overwrite
    clean = {k: v for k, v in payload.settings.items() if v != "••••••••"}
    if not clean:
        return {"message": "No settings to update", "count": 0}

    count = settings_service.bulk_update_settings(db, clean)

    log_admin_action(
        action=AuditActions.SETTINGS_UPDATED,
        admin_user_id=admin.id,
        admin_username=admin.username,
        target_type="settings",
        details={"keys_updated": list(clean.keys()), "count": count},
        ip_address=request.client.host if request.client else None
    )

    return {"message": f"Updated {count} settings", "count": count}
