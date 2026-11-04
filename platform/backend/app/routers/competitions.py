"""Opt-in special competitions.

Competitions are deliberately separate from the learning record: a learner
joins an event explicitly, only solves inside the event window count, and the
event leaderboard is time-boxed. The score reuses the course scoreboard rules
(completion, no-hint, first-attempt, speed, and competition first blood).
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_active_user, get_current_instructor_user
from app.database import get_db
from app.models import (
    Competition,
    CompetitionLab,
    CompetitionParticipant,
    Lab,
    LabCompletion,
    Level,
    User,
)
from app.routers.courses import calculate_lab_score

router = APIRouter()


class CompetitionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime
    lab_ids: List[int] = Field(..., min_length=1)


class CompetitionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    lab_ids: Optional[List[int]] = Field(None, min_length=1)
    is_active: Optional[bool] = None


def _aware(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _status(competition: Competition, now: datetime) -> str:
    if getattr(competition, "is_archived", False):
        return "archived"
    if not competition.is_active:
        return "inactive"
    if now < _aware(competition.start_at):
        return "upcoming"
    if now > _aware(competition.end_at):
        return "ended"
    return "active"


def _can_manage(competition: Competition, user: User) -> bool:
    return user.role == "admin" or competition.created_by == user.id


def _competition_or_404(db: Session, competition_id: int) -> Competition:
    competition = db.query(Competition).filter(
        Competition.id == competition_id
    ).first()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition


def _require_manage(competition: Competition, user: User):
    if not _can_manage(competition, user):
        raise HTTPException(
            status_code=403, detail="Only the organiser or an admin can change this competition"
        )


def _lab_rows(db: Session, competition_id: int):
    return db.query(CompetitionLab).options(
        joinedload(CompetitionLab.lab).joinedload(Lab.level).joinedload(Level.track)
    ).filter(
        CompetitionLab.competition_id == competition_id
    ).order_by(CompetitionLab.sort_order, CompetitionLab.id).all()


def _lab_payload(row: CompetitionLab) -> dict:
    lab = row.lab
    level = lab.level if lab and lab.level else None
    track = level.track if level and level.track else None
    # High-school content is one track of lessons, not a numbered level ladder.
    # Grade 12 material is a special lesson inside it. Neither should read as
    # "Level 12" anywhere a student sees it.
    is_high_school = bool(track and track.slug == "high-school")
    special = bool(level and "grade 12" in (level.name or "").lower())
    if is_high_school:
        level_label = None
    elif special:
        level_label = level.name if level else None
    else:
        level_label = f"Level {level.level_number}" if level else None
    return {
        "id": lab.id if lab else None,
        "name": lab.name if lab else "Removed exercise",
        "slug": lab.slug if lab else None,
        "difficulty": lab.difficulty if lab else None,
        "duration_minutes": lab.duration_minutes if lab else None,
        "track_name": track.name if track else "Uncategorized",
        "track_slug": track.slug if track else None,
        "level_name": level.name if level else "Uncategorized",
        "level_number": level.level_number if level else None,
        "level_label": level_label,
        "is_special_lesson": is_high_school or special,
        "sort_order": row.sort_order,
    }


def _summary(
    competition: Competition,
    current_user: User,
    now: datetime,
    participant_count: int,
    lab_count: int,
    joined: bool,
) -> dict:
    return {
        "id": competition.id,
        "name": competition.name,
        "description": competition.description,
        "start_at": _iso(competition.start_at),
        "end_at": _iso(competition.end_at),
        "status": _status(competition, now),
        "is_active": competition.is_active,
        "is_archived": bool(getattr(competition, "is_archived", False)),
        "participant_count": participant_count,
        "lab_count": lab_count,
        "joined": joined,
        "can_manage": _can_manage(competition, current_user),
    }


def _leaderboard(
    db: Session,
    competition: Competition,
    current_user: User,
) -> dict:
    lab_rows = _lab_rows(db, competition.id)
    labs = [row.lab for row in lab_rows if row.lab and row.lab.is_active]
    is_manager = _can_manage(competition, current_user)
    participants = db.query(CompetitionParticipant).options(
        joinedload(CompetitionParticipant.user)
    ).filter(
        CompetitionParticipant.competition_id == competition.id
    ).all()
    participants = [p for p in participants if p.user and p.user.is_active]
    # Pending accounts are visible to the organiser as new sign-ups, but they
    # do not appear on the public event leaderboard until approved.
    if not is_manager:
        participants = [p for p in participants if p.user.is_approved]

    if not participants or not labs:
        return {
            "entries": [],
            "my_entry": None,
            "registration_counts": {
                "total": len(participants),
                "new_user": sum(
                    1 for p in participants if (p.source or "opt_in") == "new_user"
                ),
                "opt_in": sum(
                    1 for p in participants if (p.source or "opt_in") == "opt_in"
                ),
            },
        }

    user_ids = [p.user_id for p in participants]
    lab_ids = [lab.id for lab in labs]
    completions = db.query(LabCompletion).filter(
        LabCompletion.user_id.in_(user_ids),
        LabCompletion.lab_id.in_(lab_ids),
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
        LabCompletion.completed_at >= competition.start_at,
        LabCompletion.completed_at <= competition.end_at,
    ).all()

    completion_map = {
        (row.user_id, row.lab_id): row for row in completions
    }
    first_blood_map = {}
    for row in completions:
        current = first_blood_map.get(row.lab_id)
        if current is None or row.completed_at < current.completed_at:
            first_blood_map[row.lab_id] = row

    entries = []
    for participant in participants:
        score = 0
        solved = 0
        last_solved = None
        for lab in labs:
            completion = completion_map.get((participant.user_id, lab.id))
            if not completion:
                continue
            first = first_blood_map.get(lab.id)
            score += calculate_lab_score(
                completion,
                lab,
                0,
                db,
                first_blood_user_id=first.user_id if first else None,
            )
            solved += 1
            if last_solved is None or completion.completed_at > last_solved:
                last_solved = completion.completed_at

        user = participant.user
        display_name = (
            user.scoreboard_name if getattr(user, "show_on_scoreboard", True)
            else "Anonymous participant"
        )
        anonymous = display_name == "Anonymous participant"
        entries.append({
            "user_id": user.id,
            "username": None if anonymous else user.username,
            "display_name": display_name,
            "score": score,
            "solved_count": solved,
            "last_solved_at": _iso(last_solved),
            "source": participant.source or "opt_in",
            "joined_at": _iso(participant.joined_at),
            "is_me": user.id == current_user.id,
            "_last": last_solved,
            "_joined": participant.joined_at,
        })

    entries.sort(
        key=lambda entry: (
            -entry["score"],
            entry["_last"] is None,
            entry["_last"] or datetime.max,
            entry["_joined"] or datetime.max,
        )
    )
    for rank, entry in enumerate(entries, 1):
        entry["rank"] = rank
        entry.pop("_last", None)
        entry.pop("_joined", None)

    registration_counts = {
        "total": len(participants),
        "new_user": sum(1 for p in participants if (p.source or "opt_in") == "new_user"),
        "opt_in": sum(1 for p in participants if (p.source or "opt_in") == "opt_in"),
    }

    # Registration source is organiser information, not public leaderboard data.
    if not is_manager:
        for entry in entries:
            entry.pop("source", None)
            entry.pop("joined_at", None)

    my_entry = next(
        (entry for entry in entries if entry["user_id"] == current_user.id), None
    )
    return {
        "entries": entries,
        "my_entry": my_entry,
        "registration_counts": registration_counts,
    }


@router.get("")
async def list_competitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List competitions. Inactive events are hidden from students."""
    query = db.query(Competition)
    if current_user.role not in ("instructor", "admin"):
        query = query.filter(Competition.is_active == True)
    competitions = query.order_by(Competition.start_at.desc()).limit(100).all()

    now = datetime.now(timezone.utc)
    competition_ids = [c.id for c in competitions]
    participant_counts = {}
    lab_counts = {}
    joined_ids = set()
    if competition_ids:
        participant_counts = dict(
            db.query(
                CompetitionParticipant.competition_id,
                func.count(CompetitionParticipant.id),
            ).filter(
                CompetitionParticipant.competition_id.in_(competition_ids)
            ).group_by(CompetitionParticipant.competition_id).all()
        )
        lab_counts = dict(
            db.query(
                CompetitionLab.competition_id,
                func.count(CompetitionLab.id),
            ).filter(
                CompetitionLab.competition_id.in_(competition_ids)
            ).group_by(CompetitionLab.competition_id).all()
        )
        joined_ids = {
            row[0] for row in db.query(CompetitionParticipant.competition_id).filter(
                CompetitionParticipant.user_id == current_user.id,
                CompetitionParticipant.competition_id.in_(competition_ids),
            ).all()
        }

    return {
        "competitions": [
            _summary(
                c,
                current_user,
                now,
                participant_counts.get(c.id, 0),
                lab_counts.get(c.id, 0),
                c.id in joined_ids,
            )
            for c in competitions
        ]
    }


@router.get("/public/{competition_id}")
async def public_competition(competition_id: int, db: Session = Depends(get_db)):
    """Minimal public event information for a competition sign-up link."""
    competition = _competition_or_404(db, competition_id)
    if not competition.is_active:
        raise HTTPException(status_code=404, detail="Competition not found")
    now = datetime.now(timezone.utc)
    return {
        "competition": {
            "id": competition.id,
            "name": competition.name,
            "description": competition.description,
            "start_at": _iso(competition.start_at),
            "end_at": _iso(competition.end_at),
            "status": _status(competition, now),
        }
    }


@router.get("/{competition_id}")
async def get_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = _competition_or_404(db, competition_id)
    if not competition.is_active and current_user.role not in ("instructor", "admin"):
        raise HTTPException(status_code=404, detail="Competition not found")

    now = datetime.now(timezone.utc)
    lab_rows = _lab_rows(db, competition_id)
    joined = db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition_id,
        CompetitionParticipant.user_id == current_user.id,
    ).first() is not None
    participant_count = db.query(func.count(CompetitionParticipant.id)).filter(
        CompetitionParticipant.competition_id == competition_id
    ).scalar() or 0

    return {
        "competition": _summary(
            competition, current_user, now, participant_count,
            len(lab_rows), joined,
        ),
        "labs": [_lab_payload(row) for row in lab_rows],
        "leaderboard": _leaderboard(db, competition, current_user),
    }


@router.post("", status_code=201)
async def create_competition(
    payload: CompetitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Competition name is required")
    if _aware(payload.end_at) <= _aware(payload.start_at):
        raise HTTPException(status_code=400, detail="End time must be after start time")

    requested_ids = list(dict.fromkeys(payload.lab_ids))
    labs = db.query(Lab).filter(
        Lab.id.in_(requested_ids), Lab.is_active == True
    ).all()
    lab_map = {lab.id: lab for lab in labs}
    missing = [lab_id for lab_id in requested_ids if lab_id not in lab_map]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown or inactive exercise IDs: {missing}",
        )

    competition = Competition(
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
        start_at=payload.start_at,
        end_at=payload.end_at,
        created_by=current_user.id,
        is_active=True,
    )
    db.add(competition)
    db.flush()
    for order, lab_id in enumerate(requested_ids):
        db.add(CompetitionLab(
            competition_id=competition.id,
            lab_id=lab_id,
            sort_order=order,
        ))
    db.commit()
    db.refresh(competition)
    return {"message": "Competition created", "id": competition.id}


@router.patch("/{competition_id}")
async def update_competition(
    competition_id: int,
    payload: CompetitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)

    start_at = payload.start_at if payload.start_at is not None else competition.start_at
    end_at = payload.end_at if payload.end_at is not None else competition.end_at
    if _aware(end_at) <= _aware(start_at):
        raise HTTPException(status_code=400, detail="End time must be after start time")

    if payload.name is not None:
        if not payload.name.strip():
            raise HTTPException(status_code=400, detail="Competition name is required")
        competition.name = payload.name.strip()
    if payload.description is not None:
        competition.description = payload.description.strip() or None
    competition.start_at = start_at
    competition.end_at = end_at
    if payload.is_active is not None:
        competition.is_active = payload.is_active

    if payload.lab_ids is not None:
        requested_ids = list(dict.fromkeys(payload.lab_ids))
        labs = db.query(Lab).filter(
            Lab.id.in_(requested_ids), Lab.is_active == True
        ).all()
        found = {lab.id for lab in labs}
        missing = [lab_id for lab_id in requested_ids if lab_id not in found]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown or inactive exercise IDs: {missing}",
            )
        db.query(CompetitionLab).filter(
            CompetitionLab.competition_id == competition.id
        ).delete()
        for order, lab_id in enumerate(requested_ids):
            db.add(CompetitionLab(
                competition_id=competition.id,
                lab_id=lab_id,
                sort_order=order,
            ))

    db.commit()
    return {"message": "Competition updated"}


@router.post("/{competition_id}/archive")
async def archive_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    """Archive an event: keep every result, hide it from the default list."""
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)
    competition.is_archived = True
    db.commit()
    return {"message": "Competition archived", "is_archived": True}


@router.post("/{competition_id}/unarchive")
async def unarchive_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)
    competition.is_archived = False
    db.commit()
    return {"message": "Competition restored", "is_archived": False}


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor_user),
):
    competition = _competition_or_404(db, competition_id)
    _require_manage(competition, current_user)
    db.delete(competition)
    db.commit()
    return {"message": "Competition deleted"}


@router.post("/{competition_id}/join")
async def join_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = _competition_or_404(db, competition_id)
    status = _status(competition, datetime.now(timezone.utc))
    if status in ("ended", "inactive", "archived"):
        raise HTTPException(status_code=400, detail="This competition is closed")
    existing = db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition_id,
        CompetitionParticipant.user_id == current_user.id,
    ).first()
    if not existing:
        db.add(CompetitionParticipant(
            competition_id=competition_id,
            user_id=current_user.id,
            source="opt_in",
        ))
        db.commit()
    return {"message": "Joined competition", "joined": True}


@router.post("/{competition_id}/leave")
async def leave_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    competition = _competition_or_404(db, competition_id)
    db.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition.id,
        CompetitionParticipant.user_id == current_user.id,
    ).delete()
    db.commit()
    return {"message": "Left competition", "joined": False}
