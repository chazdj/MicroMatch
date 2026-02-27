from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.database import get_db
from app.models import Application, Project, User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationStatusUpdate
from app.core.dependencies import require_role

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def apply_to_project(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student"))
):
    """
    Allows an authenticated student to apply to a project.

    Business Rules:
    - Only users with role "student" may apply.
    - Project must exist.
    - Student cannot apply twice to same project.
    - Application status defaults to "pending".

    Raises:
    - 404 if project does not exist
    - 400 if duplicate application
    """

    # ---------------------------------------------------------
    # Validate project exists
    # ---------------------------------------------------------
    project = db.query(Project).filter(
        Project.id == application_data.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # ---------------------------------------------------------
    # Create Application
    # ---------------------------------------------------------
    application = Application(
        student_id=current_user.id,
        project_id=application_data.project_id
    )

    db.add(application)

    try:
        db.commit()
        db.refresh(application)
    except IntegrityError:
        # Rollback required after failed commit
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this project"
        )

    return application

@router.get("/me", response_model=List[ApplicationRead], status_code=status.HTTP_200_OK)
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student"))
):
    """
    Retrieves all applications submitted by the authenticated student.

    Business Rules:
    - Only users with role "student" may access this endpoint.
    - Returns applications ordered by newest first.
    - Includes application metadata (status, timestamps).

    Returns:
    - List of ApplicationRead objects

    Raises:
    - 403 if user is not a student
    """

    # ---------------------------------------------------------
    # Query applications belonging to the current student
    # ---------------------------------------------------------
    applications = (
        db.query(Application)
        .filter(Application.student_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )

    return applications

@router.patch("/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    """
    Allows an organization to accept or reject a student's application.

    Business Rules:
    - Only users with role "organization" may update status.
    - Organization must own the related project.
    - Valid transitions:
        pending → accepted
        pending → rejected
    - Once accepted or rejected, status cannot be modified again.

    Raises:
    - 404 if application does not exist
    - 403 if organization does not own project
    - 400 for invalid status or invalid transition
    """

    # ---------------------------------------------------------
    # Validate application exists
    # ---------------------------------------------------------
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # ---------------------------------------------------------
    # Validate project ownership
    # ---------------------------------------------------------
    project = db.query(Project).filter(
        Project.id == application.project_id
    ).first()

    if project.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application"
        )

    # ---------------------------------------------------------
    # Normalize and validate status value
    # ---------------------------------------------------------
    new_status = status_update.status.lower()
    valid_statuses = ["accepted", "rejected"]

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value"
        )

    # ---------------------------------------------------------
    # Validate transition rules
    # ---------------------------------------------------------
    current_status = application.status.lower()

    if current_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application status cannot be modified"
        )

    # ---------------------------------------------------------
    # Perform update
    # ---------------------------------------------------------
    application.status = new_status
    db.commit()
    db.refresh(application)

    return application