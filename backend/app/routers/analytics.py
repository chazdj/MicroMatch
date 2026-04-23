from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Project, Application, Feedback
from app.schemas.analytics import StudentAnalytics, OrganizationAnalytics
from app.core.dependencies import require_role

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/student", response_model=StudentAnalytics)
def get_student_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Returns productivity analytics for the authenticated student.

    Metrics:
    - applications_submitted: total applications ever made
    - accepted_applications: applications with status "accepted"
    - completed_projects: projects linked to accepted applications that are "completed"
    - average_feedback_rating: mean rating across all feedback submitted by this student

    RBAC: student role only.
    """
    applications_submitted = (
        db.query(func.count(Application.id))
        .filter(Application.student_id == current_user.id)
        .scalar()
    )

    accepted_applications = (
        db.query(func.count(Application.id))
        .filter(
            Application.student_id == current_user.id,
            Application.status == "accepted",
        )
        .scalar()
    )

    completed_projects = (
        db.query(func.count(Application.id))
        .join(Project, Project.id == Application.project_id)
        .filter(
            Application.student_id == current_user.id,
            Application.status == "accepted",
            Project.status == "completed",
        )
        .scalar()
    )

    avg_rating_result = (
        db.query(func.avg(Feedback.rating))
        .filter(Feedback.user_id == current_user.id)
        .scalar()
    )
    average_feedback_rating = (
        round(float(avg_rating_result), 2) if avg_rating_result is not None else None
    )

    return StudentAnalytics(
        applications_submitted=applications_submitted,
        accepted_applications=accepted_applications,
        completed_projects=completed_projects,
        average_feedback_rating=average_feedback_rating,
    )


@router.get("/organization", response_model=OrganizationAnalytics)
def get_organization_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization")),
):
    """
    Returns productivity analytics for the authenticated organization.

    Metrics:
    - total_projects_posted: all projects ever created by this org
    - active_projects: projects with status "open"
    - completed_projects: projects with status "completed"
    - total_applicants: unique students who applied across all org projects

    RBAC: organization role only.
    """
    total_projects_posted = (
        db.query(func.count(Project.id))
        .filter(Project.organization_id == current_user.id)
        .scalar()
    )

    active_projects = (
        db.query(func.count(Project.id))
        .filter(
            Project.organization_id == current_user.id,
            Project.status == "open",
        )
        .scalar()
    )

    completed_projects = (
        db.query(func.count(Project.id))
        .filter(
            Project.organization_id == current_user.id,
            Project.status == "completed",
        )
        .scalar()
    )

    total_applicants = (
        db.query(func.count(func.distinct(Application.student_id)))
        .join(Project, Project.id == Application.project_id)
        .filter(Project.organization_id == current_user.id)
        .scalar()
    )

    return OrganizationAnalytics(
        total_projects_posted=total_projects_posted,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_applicants=total_applicants,
    )