from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.database import get_db
from app.models import Deliverable, Application, Project, User
from app.schemas.deliverable import DeliverableReview, DeliverableRead
from app.core.dependencies import require_role

router = APIRouter(
    prefix="/deliverables",
    tags=["Deliverables"]
)


@router.put("/{deliverable_id}/review", response_model=DeliverableRead)
def review_deliverable(
    deliverable_id: int,
    review_data: DeliverableReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    """
    Organization reviews a deliverable.

    Rules:
    - Only organizations
    - Deliverable must exist
    - Must belong to org's project
    - Must be in 'submitted' state
    - Cannot review twice
    """

    # ---------------------------------------------------------
    # Validate deliverable exists
    # ---------------------------------------------------------
    deliverable = db.query(Deliverable).filter(
        Deliverable.id == deliverable_id
    ).first()

    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deliverable not found"
        )

    # ---------------------------------------------------------
    # Get related application + project
    # ---------------------------------------------------------
    application = db.query(Application).filter(
        Application.id == deliverable.application_id
    ).first()

    project = db.query(Project).filter(
        Project.id == application.project_id
    ).first()

    # ---------------------------------------------------------
    # Ownership check
    # ---------------------------------------------------------
    if project.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to review this deliverable"
        )

    # ---------------------------------------------------------
    # Prevent double review
    # ---------------------------------------------------------
    if deliverable.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deliverable already reviewed"
        )

    # ---------------------------------------------------------
    # Validate status
    # ---------------------------------------------------------
    new_status = review_data.status.lower()

    if new_status not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    # ---------------------------------------------------------
    # Apply review
    # ---------------------------------------------------------
    deliverable.status = new_status
    deliverable.feedback = review_data.feedback
    deliverable.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(deliverable)

    return deliverable

@router.get("/projects/{project_id}", response_model=list[DeliverableRead])
def get_project_deliverables(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    """
    Get all deliverables for a project.

    Rules:
    - Only organizations
    - Must own the project
    """

    # ---------------------------------------------------------
    # Validate project
    # ---------------------------------------------------------
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # ---------------------------------------------------------
    # Ownership check
    # ---------------------------------------------------------
    if project.organization_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    # ---------------------------------------------------------
    # Get deliverables via applications
    # ---------------------------------------------------------
    deliverables = (
        db.query(Deliverable)
        .join(Application)
        .filter(Application.project_id == project_id)
        .options(joinedload(Deliverable.application)
                 .joinedload(Application.student)
                 )
        .all()
    )
    result = []

    for d in deliverables:
        d.student = d.application.student
        result.append(d)

    return result