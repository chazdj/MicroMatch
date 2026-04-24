from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import StudentProfile, Application, Project, Feedback


# ── Badge definitions ─────────────────────────────────────────────────────────
# Each badge: (badge_key, label, check_fn(student_id, db) -> bool)

def _completed_count(student_id: int, db: Session) -> int:
    return (
        db.query(func.count(Application.id))
        .join(Project, Project.id == Application.project_id)
        .filter(
            Application.student_id == student_id,
            Application.status == "accepted",
            Project.status == "completed",
        )
        .scalar()
    )


def _avg_rating(student_id: int, db: Session) -> float | None:
    result = (
        db.query(func.avg(Feedback.rating))
        .filter(Feedback.user_id == student_id)
        .scalar()
    )
    return float(result) if result is not None else None


BADGE_DEFINITIONS = [
    (
        "first_project",
        "First Project",
        lambda sid, db: _completed_count(sid, db) >= 1,
    ),
    (
        "three_projects",
        "3 Projects",
        lambda sid, db: _completed_count(sid, db) >= 3,
    ),
    (
        "ten_projects",
        "10 Projects",
        lambda sid, db: _completed_count(sid, db) >= 10,
    ),
    (
        "top_rated",
        "Top Rated",
        lambda sid, db: (_avg_rating(sid, db) or 0) >= 4.5,
    ),
    (
        "rising_star",
        "Rising Star",
        lambda sid, db: (
            _completed_count(sid, db) >= 3
            and (_avg_rating(sid, db) or 0) >= 4.0
        ),
    ),
]


def compute_badges(student_id: int, db: Session) -> str:
    """
    Evaluates all badge definitions against the student's current activity.
    Returns a comma-separated string of earned badge keys.
    Does NOT commit — the caller owns the transaction.
    """
    earned = [
        key
        for key, _label, check in BADGE_DEFINITIONS
        if check(student_id, db)
    ]
    return ",".join(earned)


def award_badges(student_id: int, db: Session) -> None:
    """
    Recomputes and saves badges for a student.
    Call this whenever a project is completed or feedback is submitted.
    Does NOT commit — the caller owns the transaction.
    """
    profile = db.query(StudentProfile).filter_by(user_id=student_id).first()
    if not profile:
        return

    profile.badges = compute_badges(student_id, db)