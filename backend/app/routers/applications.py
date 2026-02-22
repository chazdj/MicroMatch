from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Application, Project, User
from app.schemas.application import ApplicationCreate, ApplicationRead
from app.core.dependencies import require_role

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


@router.post(
    "",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED
)
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