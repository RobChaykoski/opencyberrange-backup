"""
Achievement checking and awarding logic.
Called after successful flag submissions to award micro-credentials.
"""

import logging
from sqlalchemy.orm import Session
from app.models import (
    Achievement, CourseEnrollment, CourseLabAssignment,
    CourseCompletionReset, Lab, Level, LabCompletion, CustomAchievement, Track
)
from app.services.activity import log_activity, EventTypes

logger = logging.getLogger(__name__)

# Achievement type constants
FIRST_BLOOD = "first_blood"
NO_HINTS = "no_hints"
PERFECTIONIST = "perfectionist"
SPEED_DEMON = "speed_demon"
CLEAN_SWEEP = "clean_sweep"
STREAK = "streak"
SHELL_SHOCKED = "shell_shocked"
SOURCE_WHISPERER = "source_whisperer"
MEMORY_MINER = "memory_miner"
GHOST_IN_THE_RAM = "ghost_in_the_ram"
VOICE_FROM_THE_WIRE = "voice_from_the_wire"
SIP_WHISPERER = "sip_whisperer"
RANGEBOX_ROOKIE = "rangebox_rookie"
FILE_HUNTER = "file_hunter"
HEADER_HUNTER = "header_hunter"
SOURCE_SLEUTH = "source_sleuth"
LOG_DETECTIVE = "log_detective"
RANGEBOX_RANGER = "rangebox_ranger"
FORENSICS_PATHFINDER = "forensics_pathfinder"

ACHIEVEMENT_LABELS = {
    FIRST_BLOOD: "First Blood",
    NO_HINTS: "Self-Reliant",
    PERFECTIONIST: "Perfectionist",
    SPEED_DEMON: "Speed Demon",
    CLEAN_SWEEP: "Clean Sweep",
    STREAK: "On a Roll",
    SHELL_SHOCKED: "Shell Shocked",
    SOURCE_WHISPERER: "Source Whisperer",
    MEMORY_MINER: "Memory Miner",
    GHOST_IN_THE_RAM: "Ghost in the RAM",
    VOICE_FROM_THE_WIRE: "Voice from the Wire",
    SIP_WHISPERER: "SIP Whisperer",
    RANGEBOX_ROOKIE: "RangeBox Rookie",
    FILE_HUNTER: "File Hunter",
    HEADER_HUNTER: "Header Hunter",
    SOURCE_SLEUTH: "Source Sleuth",
    LOG_DETECTIVE: "Log Detective",
    RANGEBOX_RANGER: "RangeBox Ranger",
    FORENSICS_PATHFINDER: "Forensics Pathfinder",
}

ACHIEVEMENT_DESCRIPTIONS = {
    FIRST_BLOOD: "First student in the course to complete this lab",
    NO_HINTS: "Completed a lab without using any hints",
    PERFECTIONIST: "Completed a lab on the first flag attempt",
    SPEED_DEMON: "Completed a lab in under half the estimated time",
    CLEAN_SWEEP: "Completed all assigned labs in the course",
    STREAK: "Completed 3+ labs in a row with no hints and first attempt",
    SHELL_SHOCKED: "Found the command-injection bug and captured the flag on the first attempt without hints",
    SOURCE_WHISPERER: "Found the hidden export route without using hints",
    MEMORY_MINER: "Completed the Windows memory analysis lab",
    GHOST_IN_THE_RAM: "Completed the memory lab without using hints",
    VOICE_FROM_THE_WIRE: "Reconstructed the VoIP call and captured the flag",
    SIP_WHISPERER: "Completed the VoIP lab without hints on the first attempt",
    RANGEBOX_ROOKIE: "Completed the first RangeBox exercise",
    FILE_HUNTER: "Completed the RangeBox file hunt",
    HEADER_HUNTER: "Completed the RangeBox network basics lab",
    SOURCE_SLEUTH: "Completed the RangeBox browser and source lab",
    LOG_DETECTIVE: "Read the access log and captured the flag",
    RANGEBOX_RANGER: "Completed all four RangeBox basics exercises",
    FORENSICS_PATHFINDER: "Completed both Digital Forensics exercises",
}

# The three browser-first DevFest starter exercises. These slugs are stable;
# the hidden DevFest achievement uses them rather than a track-wide count.
DEVFEST_LAB_SLUGS = (
    "high-school-12-1-devfest-community-portal",
    "software-security-1-1-hidden-export-route",
    "software-security-2-1-diagnostics-command-injection",
)

# RangeBox basics and Digital Forensics collections. The collection badges are
# global, so they are reachable whether the exercises are assigned to a course
# or played as standalone labs.
RANGEBOX_BASIC_LAB_SLUGS = (
    "high-school-9-1-rangebox-first-steps",
    "high-school-9-2-rangebox-file-hunt",
    "high-school-10-1-rangebox-network-basics",
    "high-school-10-2-rangebox-browser-and-source",
)

FORENSICS_LAB_SLUGS = (
    "forensics-1-1-windows-memory-volatility",
    "forensics-2-1-voip-call-reconstruction",
)

# Triggers available to admin-defined achievements. The value is what the
# settings UI shows; the evaluator below implements each one.
CUSTOM_ACHIEVEMENT_TRIGGERS = {
    "labs_completed": "Complete N exercises in the course",
    "no_hint_labs": "Complete N exercises without using hints",
    "perfect_labs": "Complete N exercises on the first attempt",
    "course_completed": "Complete every exercise assigned to the course",
    "osint_labs_completed": "Complete N OSINT exercises in the course",
    "osint_no_hint_labs": "Complete N OSINT exercises without using hints",
    "osint_perfect_labs": "Complete N OSINT exercises on the first attempt",
    "osint_track_completed": "Complete every assigned OSINT exercise in the course",
    "software_security_labs": "Complete N Software Security exercises",
    "software_security_no_hint_labs": "Complete N Software Security exercises without hints",
    "devfest_labs": "Complete N DevFest starter exercises",
    "devfest_no_hint_labs": "Complete N DevFest starter exercises without hints",
    "comeback_labs": "Complete N exercises after 5 or more flag attempts",
    "night_labs": "Complete N exercises between 00:00 and 05:00",
    "all_tracks_completed": "Complete at least one exercise in every active track",
}

BUILTIN_ACHIEVEMENT_ICONS = {
    FIRST_BLOOD: "\U0001F3AF",
    NO_HINTS: "\U0001F9E0",
    PERFECTIONIST: "\u2B50",
    SPEED_DEMON: "\u26A1",
    CLEAN_SWEEP: "\U0001F3C6",
    STREAK: "\U0001F525",
    SHELL_SHOCKED: "\U0001F4A5",
    SOURCE_WHISPERER: "\U0001F50E",
    MEMORY_MINER: "\U0001F9E0",
    GHOST_IN_THE_RAM: "\U0001F47B",
    VOICE_FROM_THE_WIRE: "\U0001F399\uFE0F",
    SIP_WHISPERER: "\U0001F4DE",
    RANGEBOX_ROOKIE: "\U0001F579\uFE0F",
    FILE_HUNTER: "\U0001F5C2\uFE0F",
    HEADER_HUNTER: "\U0001F4E1",
    SOURCE_SLEUTH: "\U0001F50E",
    LOG_DETECTIVE: "\U0001F4DC",
    RANGEBOX_RANGER: "\U0001F3D5\uFE0F",
    FORENSICS_PATHFINDER: "\U0001F9ED",
}


def custom_achievement_type(custom_id: int) -> str:
    """Achievement type stored for an admin-defined achievement."""
    return f"custom_{custom_id}"


def custom_achievement_id(achievement_type: str) -> int | None:
    """Return the definition ID for a ``custom_<id>`` award type."""
    if not achievement_type.startswith("custom_"):
        return None
    try:
        return int(achievement_type.split("_", 1)[1])
    except (ValueError, IndexError):
        return None


# Kept for the existing internal call sites; new code should use the public
# helper above.
_custom_id_from_type = custom_achievement_id


def resolve_achievement_label(db: Session, achievement_type: str) -> str:
    """Human label for a built-in or admin-defined achievement."""
    if achievement_type in ACHIEVEMENT_LABELS:
        return ACHIEVEMENT_LABELS[achievement_type]
    custom_id = _custom_id_from_type(achievement_type)
    if custom_id is not None:
        row = db.query(CustomAchievement).filter(
            CustomAchievement.id == custom_id
        ).first()
        if row:
            return row.name
    return achievement_type


def resolve_achievement_icon(db: Session, achievement_type: str) -> str:
    """Emoji icon for a built-in or admin-defined achievement."""
    if achievement_type in BUILTIN_ACHIEVEMENT_ICONS:
        return BUILTIN_ACHIEVEMENT_ICONS[achievement_type]
    custom_id = _custom_id_from_type(achievement_type)
    if custom_id is not None:
        row = db.query(CustomAchievement).filter(
            CustomAchievement.id == custom_id
        ).first()
        if row and row.icon:
            return row.icon
    return "\U0001F3C5"


def _award(db: Session, user_id: int, course_id: int | None, lab_id: int | None, achievement_type: str):
    """Award an achievement if not already awarded (idempotent)."""
    query = db.query(Achievement).filter(
        Achievement.user_id == user_id,
        Achievement.course_id == course_id,
        Achievement.achievement_type == achievement_type,
    )
    if lab_id is not None:
        query = query.filter(Achievement.lab_id == lab_id)
    else:
        query = query.filter(Achievement.lab_id.is_(None))

    if query.first():
        return

    db.add(Achievement(
        user_id=user_id,
        course_id=course_id,
        lab_id=lab_id,
        achievement_type=achievement_type,
    ))
    logger.info(
        f"Awarded {achievement_type} to user {user_id} "
        f"(course {course_id}) for lab {lab_id}"
    )
    log_activity(db, EventTypes.ACHIEVEMENT_AWARDED,
                  actor_id=user_id, target_type="achievement",
                  target_id=lab_id,
                  target_label=resolve_achievement_label(db, achievement_type),
                  commit=False)


def _check_lab_badges(
    db: Session,
    user_id: int,
    course_id: int | None,
    lab: Lab,
    completion: LabCompletion,
):
    """Award the hidden per-lab badges for the RangeBox and Forensics labs."""
    if lab.slug == "forensics-1-1-windows-memory-volatility":
        _award(db, user_id, course_id, lab.id, MEMORY_MINER)
        if completion.hints_used == 0:
            _award(db, user_id, course_id, lab.id, GHOST_IN_THE_RAM)
    elif lab.slug == "forensics-2-1-voip-call-reconstruction":
        _award(db, user_id, course_id, lab.id, VOICE_FROM_THE_WIRE)
        if completion.hints_used == 0 and completion.attempts == 1:
            _award(db, user_id, course_id, lab.id, SIP_WHISPERER)
    elif lab.slug == "high-school-9-1-rangebox-first-steps":
        _award(db, user_id, course_id, lab.id, RANGEBOX_ROOKIE)
    elif lab.slug == "high-school-9-2-rangebox-file-hunt":
        _award(db, user_id, course_id, lab.id, FILE_HUNTER)
    elif lab.slug == "high-school-10-1-rangebox-network-basics":
        _award(db, user_id, course_id, lab.id, HEADER_HUNTER)
    elif lab.slug == "high-school-10-2-rangebox-browser-and-source":
        _award(db, user_id, course_id, lab.id, SOURCE_SLEUTH)
    elif lab.slug == "high-school-11-1-rangebox-log-detective":
        _award(db, user_id, course_id, lab.id, LOG_DETECTIVE)

    # Existing hidden software-security badges.
    if (lab.slug == "software-security-2-1-diagnostics-command-injection"
            and completion.hints_used == 0
            and completion.attempts == 1):
        _award(db, user_id, course_id, lab.id, SHELL_SHOCKED)
    if (lab.slug == "software-security-1-1-hidden-export-route"
            and completion.hints_used == 0):
        _award(db, user_id, course_id, lab.id, SOURCE_WHISPERER)


def _check_collection_achievements(db: Session, user_id: int):
    """Award global collection badges for the new lab families."""
    completed = {
        row[0] for row in db.query(LabCompletion.lab_id).filter(
            LabCompletion.user_id == user_id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        ).all()
    }
    if not completed:
        return

    def _lab_ids(slugs):
        return {
            row[0] for row in db.query(Lab.id).filter(Lab.slug.in_(slugs)).all()
        }

    rangebox_ids = _lab_ids(RANGEBOX_BASIC_LAB_SLUGS)
    if rangebox_ids and rangebox_ids.issubset(completed):
        _award(db, user_id, None, None, RANGEBOX_RANGER)

    forensics_ids = _lab_ids(FORENSICS_LAB_SLUGS)
    if forensics_ids and forensics_ids.issubset(completed):
        _award(db, user_id, None, None, FORENSICS_PATHFINDER)


def check_achievements(db: Session, user_id: int, lab_id: int):
    """Award course-scoped and global achievements for a completed lab.

    Course-scoped badges keep their per-course semantics. A lab that is not
    part of any course the student is enrolled in still awards the global
    badges (hidden lab badges and admin-defined achievements); otherwise a
    student playing standalone labs or a DevFest competition would earn
    nothing, making the hidden set unreachable.

    Called after a successful flag submission and db.commit().
    """
    completion = db.query(LabCompletion).filter(
        LabCompletion.user_id == user_id,
        LabCompletion.lab_id == lab_id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).first()

    if not completion:
        return

    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        return

    # Courses where the user is enrolled
    course_ids = {
        r[0] for r in db.query(CourseEnrollment.course_id).filter(
            CourseEnrollment.user_id == user_id
        ).all()
    }

    assignments = []
    if course_ids:
        assignments = db.query(CourseLabAssignment).filter(
            CourseLabAssignment.course_id.in_(course_ids),
            CourseLabAssignment.lab_id == lab_id,
        ).all()

    if not assignments:
        _check_global_achievements(db, user_id, lab, completion)
        db.commit()
        return

    for assignment in assignments:
        course_id = assignment.course_id

        # Get enrollment date and resets for course-aware filtering
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == user_id,
        ).first()
        if not enrollment:
            continue
        enrolled_at = enrollment.enrolled_at

        # Build reset map for this user+course
        resets = db.query(CourseCompletionReset).filter(
            CourseCompletionReset.course_id == course_id,
            CourseCompletionReset.user_id == user_id,
        ).all()
        reset_map = {}
        for r in resets:
            if r.lab_id not in reset_map or r.reset_at > reset_map[r.lab_id]:
                reset_map[r.lab_id] = r.reset_at

        def _valid_in_course(c, enrolled_at=enrolled_at, reset_map=reset_map):
            """Check if a completion counts in this course context."""
            if not c or not c.completed_at or not c.flag_submitted:
                return False
            if c.completed_at < enrolled_at:
                return False
            lr = reset_map.get(c.lab_id)
            if lr and c.completed_at <= lr:
                return False
            return True

        # Verify current completion is valid in this course
        if not _valid_in_course(completion):
            continue

        # --- first_blood: first in course to complete this lab (course-aware) ---
        all_enrolled_ids = [
            r[0] for r in db.query(CourseEnrollment.user_id).filter(
                CourseEnrollment.course_id == course_id
            ).all()
        ]
        all_completions = db.query(LabCompletion).filter(
            LabCompletion.user_id.in_(all_enrolled_ids),
            LabCompletion.lab_id == lab_id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        ).all()

        # Build per-user enrollment dates and resets for first_blood
        enrollment_dates = {
            r.user_id: r.enrolled_at
            for r in db.query(CourseEnrollment).filter(
                CourseEnrollment.course_id == course_id
            ).all()
        }
        all_resets = db.query(CourseCompletionReset).filter(
            CourseCompletionReset.course_id == course_id,
            CourseCompletionReset.lab_id == lab_id,
        ).all()
        all_reset_map = {}
        for r in all_resets:
            key = r.user_id
            if key not in all_reset_map or r.reset_at > all_reset_map[key]:
                all_reset_map[key] = r.reset_at

        first_completer_id = None
        earliest_time = None
        for c in all_completions:
            uid = c.user_id
            ea = enrollment_dates.get(uid)
            if not ea or not c.completed_at or c.completed_at < ea:
                continue
            lr = all_reset_map.get(uid)
            if lr and c.completed_at <= lr:
                continue
            if earliest_time is None or c.completed_at < earliest_time:
                earliest_time = c.completed_at
                first_completer_id = uid

        if first_completer_id == user_id:
            _award(db, user_id, course_id, lab_id, FIRST_BLOOD)

        # --- no_hints: completed with 0 hints ---
        if completion.hints_used == 0:
            _award(db, user_id, course_id, lab_id, NO_HINTS)

        # --- perfectionist: completed on first attempt ---
        if completion.attempts == 1:
            _award(db, user_id, course_id, lab_id, PERFECTIONIST)

        # --- speed_demon: under half the estimated time ---
        if (completion.time_spent_minutes
                and lab.duration_minutes
                and completion.time_spent_minutes < lab.duration_minutes * 0.5):
            _award(db, user_id, course_id, lab_id, SPEED_DEMON)

        # --- hidden per-lab badges (RangeBox, Forensics, Software Security) ---
        _check_lab_badges(db, user_id, course_id, lab, completion)

        # --- clean_sweep: all assigned labs in course completed (course-aware) ---
        course_lab_ids = {
            a.lab_id for a in db.query(CourseLabAssignment).filter(
                CourseLabAssignment.course_id == course_id
            ).all()
        }
        from app.routers.courses import get_course_completed_lab_ids
        user_completed = get_course_completed_lab_ids(db, user_id, course_id, course_lab_ids)
        if course_lab_ids and course_lab_ids.issubset(user_completed):
            _award(db, user_id, course_id, None, CLEAN_SWEEP)

        # --- streak: 3+ completions in a row, all no hints + first attempt (course-aware) ---
        recent_all = db.query(LabCompletion).filter(
            LabCompletion.user_id == user_id,
            LabCompletion.lab_id.in_(course_lab_ids),
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        ).order_by(LabCompletion.completed_at.desc()).all()

        recent_valid = [c for c in recent_all if _valid_in_course(c)][:3]

        if (len(recent_valid) >= 3
                and all(c.hints_used == 0 and c.attempts == 1 for c in recent_valid)):
            _award(db, user_id, course_id, None, STREAK)

        # --- admin-defined achievements ---
        valid_completions = [c for c in recent_all if _valid_in_course(c)]
        _check_custom_achievements(
            db, user_id, course_id, course_lab_ids, valid_completions,
        )

    _check_collection_achievements(db, user_id)

    db.commit()


def _check_global_achievements(
    db: Session, user_id: int, lab: Lab, completion: LabCompletion
):
    """Awards that are not tied to a course enrolment.

    Runs when the completed lab is not assigned to any course the student is
    enrolled in: standalone public labs and competition challenges. The same
    admin-defined definitions are evaluated with a global scope (NULL
    ``course_id``) so DevFest Ghost, Range Cartographer, and the hidden lab
    badges are reachable without a course.
    """
    completions = db.query(LabCompletion).filter(
        LabCompletion.user_id == user_id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).all()

    # Hidden lab badges are per-lab, not per-course.
    _check_lab_badges(db, user_id, None, lab, completion)

    active_lab_ids = {
        row[0] for row in db.query(Lab.id).filter(Lab.is_active == True).all()
    }
    _check_collection_achievements(db, user_id)
    _check_custom_achievements(db, user_id, None, active_lab_ids, completions)


def _track_lab_ids(db: Session, track_slug: str) -> set:
    """All lab IDs in one track, used by hidden track-specific badges."""
    return {
        row[0] for row in db.query(Lab.id).join(
            Level, Lab.level_id == Level.id
        ).join(
            Track, Level.track_id == Track.id
        ).filter(Track.slug == track_slug).all()
    }


def _all_tracks_completed(db: Session, user_id: int) -> bool:
    """True when the user has completed at least one lab in every active track.

    Only tracks that currently contain active labs count, so an empty future
    track cannot make the badge impossible to earn.
    """
    active_track_ids = {
        row[0] for row in db.query(Track.id).join(
            Level, Level.track_id == Track.id
        ).join(
            Lab, Lab.level_id == Level.id
        ).filter(
            Track.is_active == True,
            Lab.is_active == True,
        ).distinct().all()
    }
    if not active_track_ids:
        return False

    completed_track_ids = {
        row[0] for row in db.query(Track.id).join(
            Level, Level.track_id == Track.id
        ).join(
            Lab, Lab.level_id == Level.id
        ).join(
            LabCompletion, LabCompletion.lab_id == Lab.id
        ).filter(
            LabCompletion.user_id == user_id,
            LabCompletion.flag_submitted.isnot(None),
            LabCompletion.flag_submitted != "",
        ).distinct().all()
    }
    return active_track_ids.issubset(completed_track_ids)


def _check_custom_achievements(
    db: Session,
    user_id: int,
    course_id: int | None,
    course_lab_ids: set,
    valid_completions: list,
):
    """Evaluate the admin-defined achievements for one user and course.

    Definitions are global (they apply to every course); an award is still
    scoped to the course, so the same definition can be earned once per course.
    """
    definitions = db.query(CustomAchievement).filter(
        CustomAchievement.is_active == True
    ).all()
    if not definitions:
        return

    labs_completed = len(valid_completions)
    no_hint_labs = sum(1 for c in valid_completions if c.hints_used == 0)
    perfect_labs = sum(1 for c in valid_completions if c.attempts == 1)
    completed_lab_ids = {c.lab_id for c in valid_completions}
    course_completed = bool(course_lab_ids) and course_lab_ids.issubset(completed_lab_ids)

    # OSINT-specific progress. The trigger uses the track slug rather than a
    # hard-coded lab list so future OSINT exercises count automatically.
    osint_lab_ids = {
        row[0] for row in db.query(Lab.id).join(
            Level, Lab.level_id == Level.id
        ).join(
            Track, Level.track_id == Track.id
        ).filter(Track.slug == "osint").all()
    }
    osint_completions = [c for c in valid_completions if c.lab_id in osint_lab_ids]
    osint_labs_completed = len(osint_completions)
    osint_no_hint_labs = sum(1 for c in osint_completions if c.hints_used == 0)
    osint_perfect_labs = sum(1 for c in osint_completions if c.attempts == 1)
    osint_assigned_lab_ids = course_lab_ids & osint_lab_ids
    osint_track_completed = (
        bool(osint_assigned_lab_ids)
        and osint_assigned_lab_ids.issubset(completed_lab_ids)
    )

    software_security_lab_ids = _track_lab_ids(db, "software-security")
    software_security_completions = [
        c for c in valid_completions if c.lab_id in software_security_lab_ids
    ]
    software_security_labs = len(software_security_completions)
    software_security_no_hints = sum(
        1 for c in software_security_completions if c.hints_used == 0
    )

    devfest_lab_ids = {
        row[0] for row in db.query(Lab.id).filter(
            Lab.slug.in_(DEVFEST_LAB_SLUGS)
        ).all()
    }
    devfest_completions = [
        c for c in valid_completions if c.lab_id in devfest_lab_ids
    ]
    devfest_labs = len(devfest_completions)
    devfest_no_hints = sum(1 for c in devfest_completions if c.hints_used == 0)

    comeback_labs = sum(1 for c in valid_completions if (c.attempts or 0) >= 5)
    night_labs = sum(
        1 for c in valid_completions
        if c.completed_at and 0 <= c.completed_at.hour < 5
    )
    all_tracks_completed = _all_tracks_completed(db, user_id)

    for definition in definitions:
        if definition.trigger == "no_hint_labs":
            reached = no_hint_labs >= (definition.threshold or 1)
        elif definition.trigger == "perfect_labs":
            reached = perfect_labs >= (definition.threshold or 1)
        elif definition.trigger == "course_completed":
            reached = course_completed
        elif definition.trigger == "osint_labs_completed":
            reached = osint_labs_completed >= (definition.threshold or 1)
        elif definition.trigger == "osint_no_hint_labs":
            reached = osint_no_hint_labs >= (definition.threshold or 1)
        elif definition.trigger == "osint_perfect_labs":
            reached = osint_perfect_labs >= (definition.threshold or 1)
        elif definition.trigger == "osint_track_completed":
            reached = osint_track_completed
        elif definition.trigger == "software_security_labs":
            reached = software_security_labs >= (definition.threshold or 1)
        elif definition.trigger == "software_security_no_hint_labs":
            reached = software_security_no_hints >= (definition.threshold or 1)
        elif definition.trigger == "devfest_labs":
            reached = devfest_labs >= (definition.threshold or 1)
        elif definition.trigger == "devfest_no_hint_labs":
            reached = devfest_no_hints >= (definition.threshold or 1)
        elif definition.trigger == "comeback_labs":
            reached = comeback_labs >= (definition.threshold or 1)
        elif definition.trigger == "night_labs":
            reached = night_labs >= (definition.threshold or 1)
        elif definition.trigger == "all_tracks_completed":
            reached = all_tracks_completed
        else:  # labs_completed (default)
            reached = labs_completed >= (definition.threshold or 1)

        if reached:
            _award(
                db, user_id, course_id, None,
                custom_achievement_type(definition.id),
            )
