from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.database import get_db
from app.models import (
    User, StudentProfile, Project,
    Application, Deliverable, Feedback
)
from app.schemas.recommendation import RecommendationItem
from app.core.dependencies import require_role
from app.services.matching_engine import (
    StudentDTO, ProjectDTO, rank_projects, parse_skills
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _build_student_dto(
    current_user: User,
    profile: StudentProfile,
    db: Session,
) -> StudentDTO:
    """
    Assembles a StudentDTO from ORM objects.
    All DB queries needed to populate the DTO happen here,
    keeping the engine itself free of SQLAlchemy dependencies.
    """

    student_id = current_user.id

    # ── Completed project count ───────────────────────────────────────────
    # A project is "completed by this student" when their application was
    # accepted AND the project status is "completed".
    completed_count = (
        db.query(Application)
        .join(Project, Project.id == Application.project_id)
        .filter(
            Application.student_id == student_id,
            Application.status == "accepted",
            Project.status == "completed",
        )
        .count()
    )

    # ── Total ever-accepted count ─────────────────────────────────────────
    total_accepted = (
        db.query(Application)
        .filter(
            Application.student_id == student_id,
            Application.status == "accepted",
        )
        .count()
    )

    # ── Accepted deliverable count ────────────────────────────────────────
    accepted_deliverables = (
        db.query(Deliverable)
        .join(Application, Application.id == Deliverable.application_id)
        .filter(
            Application.student_id == student_id,
            Deliverable.status == "accepted",
        )
        .count()
    )

    # ── Average feedback rating ───────────────────────────────────────────
    rating_result = (
        db.query(func.avg(Feedback.rating))
        .filter(Feedback.user_id == student_id)
        .scalar()
    )
    avg_rating = float(rating_result) if rating_result is not None else 0.0

    # ── Recent application count (last 30 days) ───────────────────────────
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_apps = (
        db.query(Application)
        .filter(
            Application.student_id == student_id,
            Application.created_at >= thirty_days_ago,
        )
        .count()
    )

    return StudentDTO(
        student_id=student_id,
        skills=parse_skills(profile.skills),
        major=profile.major or "",
        bio=profile.bio or "",
        completed_project_count=completed_count,
        total_accepted_count=total_accepted,
        accepted_deliverable_count=accepted_deliverables,
        average_feedback_rating=avg_rating,
        recent_application_count=recent_apps,
        graduation_year=profile.graduation_year,
    )


def _build_project_dto(project: Project) -> ProjectDTO:
    """Maps a Project ORM object to a ProjectDTO."""
    return ProjectDTO(
        project_id=project.id,
        title=project.title,
        description=project.description or "",
        required_skills=parse_skills(project.required_skills),
        duration=project.duration or "",
        status=project.status,
    )


@router.get("", response_model=List[RecommendationItem], status_code=status.HTTP_200_OK)
def get_recommendations(
    top_n: Optional[int] = Query(default=None, ge=1, le=100, description="Limit results to top N matches"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Returns ranked project recommendations for the authenticated student.

    Business Rules:
    - Only students may access this endpoint (organizations → 403).
    - Student must have a profile; returns 404 if not found.
    - Only open projects are scored and returned.
    - Projects are ranked by match score descending.
    - Returns empty list if no open projects exist — not an error.
    - Optional top_n query param slices to the N best matches (1–100).

    Query Params:
    - top_n (optional): Return only the top N results. Default: all results.

    Returns:
    - List of RecommendationItem, sorted by match_score descending.

    Raises:
    - 401 if not authenticated
    - 403 if user is not a student
    - 404 if student profile does not exist
    """

    # ── Require student profile ───────────────────────────────────────────
    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please create a profile before requesting recommendations."
        )

    # ── Load only open projects ───────────────────────────────────────────
    # Excludes closed, completed, and disabled projects.
    open_projects = (
        db.query(Project)
        .filter(Project.status == "open")
        .all()
    )

    # Empty project list — return gracefully, not an error
    if not open_projects:
        return []

    # ── Build DTOs ────────────────────────────────────────────────────────
    student_dto = _build_student_dto(current_user, profile, db)
    project_dtos = [_build_project_dto(p) for p in open_projects]

    # ── Run matching engine ───────────────────────────────────────────────
    ranked = rank_projects(student_dto, project_dtos, top_n=top_n)

    # ── Map ScoredProject → RecommendationItem ────────────────────────────
    return [
        RecommendationItem(
            project_id=r.project_id,
            title=r.title,
            match_score=r.match_score,
            rank=r.rank,
            skill_score=r.skill_score,
            experience_score=r.experience_score,
            interest_score=r.interest_score,
            activity_score=r.activity_score,
            success_score=r.success_score,
        )
        for r in ranked
    ]