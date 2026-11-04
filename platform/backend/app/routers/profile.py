"""Profile summary and printable transcript endpoints.

The profile page needs one authoritative view of a student's completion
record: the same certificate IDs the certificate page issues, the labs behind
them, and the achievements earned in courses. The PDF endpoint renders that
same payload so the on-screen profile and the downloaded document cannot drift
apart.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from app.ratelimit import create_limiter
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_active_user
from app.database import get_db
from app.models import (
    Achievement,
    Course,
    CourseEnrollment,
    Lab,
    LabCompletion,
    Level,
    Track,
    User,
)
from app.routers.curriculum import (
    _is_lab_visible,
    build_level_certificate,
    get_accessible_exclusive_lab_ids,
    get_user_completions,
)
from app.services.achievements import (
    ACHIEVEMENT_DESCRIPTIONS,
    resolve_achievement_icon,
    resolve_achievement_label,
)
from app.services.profile_report import generate_profile_transcript

router = APIRouter()
limiter = create_limiter()


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _build_profile_summary(db: Session, current_user: User) -> dict:
    """Collect certificates, completion details, and course achievements."""
    tracks = db.query(Track).options(
        joinedload(Track.levels).joinedload(Level.labs)
    ).filter(Track.is_active == True).order_by(Track.sort_order, Track.id).all()

    completed_ids = get_user_completions(db, current_user.id)
    accessible_course_lab_ids = get_accessible_exclusive_lab_ids(db, current_user.id)

    completion_rows = db.query(LabCompletion).options(
        joinedload(LabCompletion.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        LabCompletion.user_id == current_user.id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()
    completion_by_lab = {row.lab_id: row for row in completion_rows}

    certificates = []
    track_summaries = []
    completion_details = []
    total_labs = 0
    total_completed = 0

    for track in tracks:
        track_total = 0
        track_completed = 0
        level_summaries = []

        for level in sorted(track.levels, key=lambda item: item.level_number):
            visible_labs = [
                lab for lab in sorted(level.labs, key=lambda item: (item.sort_order or 0, item.id))
                if _is_lab_visible(lab, current_user, accessible_course_lab_ids)
            ]
            if not visible_labs:
                continue

            completed_labs = [lab for lab in visible_labs if lab.id in completed_ids]
            track_total += len(visible_labs)
            track_completed += len(completed_labs)
            total_labs += len(visible_labs)
            total_completed += len(completed_labs)

            certificate = build_level_certificate(
                db,
                current_user,
                track,
                level,
                visible_labs,
                completed_ids,
                include_qr=False,
            )
            if certificate:
                certificates.append(certificate)

            for lab in visible_labs:
                row = completion_by_lab.get(lab.id)
                if not row:
                    continue
                completion_details.append({
                    "lab_id": lab.id,
                    "lab_name": lab.name,
                    "lab_slug": lab.slug,
                    "difficulty": lab.difficulty,
                    "track_name": track.name,
                    "track_slug": track.slug,
                    "level_number": level.level_number,
                    "level_name": level.name,
                    "completed_at": _iso(row.completed_at),
                    "attempts": row.attempts or 0,
                    "hints_used": row.hints_used or 0,
                    "time_spent_minutes": row.time_spent_minutes,
                })

            level_summaries.append({
                "id": level.id,
                "level_number": level.level_number,
                "level_name": level.name,
                "total_labs": len(visible_labs),
                "completed_labs": len(completed_labs),
                "is_complete": len(completed_labs) == len(visible_labs),
                "certificate_id": certificate["certificate_id"] if certificate else None,
            })

        if track_total == 0:
            continue

        track_summaries.append({
            "track_id": track.id,
            "track_name": track.name,
            "track_slug": track.slug,
            "track_color": track.color,
            "total_labs": track_total,
            "completed_labs": track_completed,
            "progress_percent": round(track_completed / track_total * 100) if track_total else 0,
            "is_complete": track_completed == track_total,
            "levels": level_summaries,
        })

    certificates.sort(key=lambda item: item.get("issued_on") or "", reverse=True)
    completion_details.sort(
        key=lambda item: item.get("completed_at") or "", reverse=True
    )

    achievement_rows = db.query(Achievement).options(
        joinedload(Achievement.course),
        joinedload(Achievement.lab),
    ).filter(
        Achievement.user_id == current_user.id
    ).order_by(Achievement.awarded_at.desc()).all()

    achievements = []
    for row in achievement_rows:
        achievements.append({
            "id": row.id,
            "type": row.achievement_type,
            "label": resolve_achievement_label(db, row.achievement_type),
            "icon": resolve_achievement_icon(db, row.achievement_type),
            "description": ACHIEVEMENT_DESCRIPTIONS.get(row.achievement_type),
            "lab_name": row.lab.name if row.lab else None,
            "course_name": row.course.name if row.course else None,
            "course_code": row.course.code if row.course else None,
            "awarded_at": _iso(row.awarded_at),
        })

    enrollment_rows = db.query(Course, CourseEnrollment).join(
        CourseEnrollment,
        CourseEnrollment.course_id == Course.id,
    ).filter(
        CourseEnrollment.user_id == current_user.id,
    ).order_by(Course.name).all()

    courses = [{
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "semester": course.semester,
        "is_active": course.is_active,
        "is_archived": course.is_archived,
    } for course, _enrollment in enrollment_rows]

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "student_id": current_user.student_id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "display_name": current_user.display_name,
            "organization": current_user.organization,
            "role": current_user.role,
            "created_at": _iso(current_user.created_at),
            "avatar_data": getattr(current_user, "avatar_data", None),
        },
        "totals": {
            "labs_total": total_labs,
            "labs_completed": total_completed,
            "progress_percent": round(total_completed / total_labs * 100) if total_labs else 0,
            "certificates": len(certificates),
            "tracks": len(track_summaries),
            "achievements": len(achievements),
        },
        "certificates": certificates,
        "tracks": track_summaries,
        "completions": completion_details,
        "achievements": achievements,
        "courses": courses,
    }


@router.get("/summary", summary="Profile snapshot with certificates and completions")
@limiter.limit("60/minute")
async def profile_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return everything the profile page renders in one round trip."""
    return JSONResponse(
        content=_build_profile_summary(db, current_user),
        headers={"Cache-Control": "no-store"},
    )


@router.get("/transcript.pdf", summary="Download a printable completion transcript")
@limiter.limit("10/minute")
async def profile_transcript_pdf(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Render the profile summary as a PDF transcript."""
    summary = _build_profile_summary(db, current_user)
    pdf_bytes = generate_profile_transcript(summary, current_user.timezone)
    filename = f"OpenCyberRange-Transcript-{current_user.username}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
