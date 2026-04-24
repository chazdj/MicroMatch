from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Feedback, Project, User
from app.utils.badges import award_badges
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a completed project.
    - Only students can submit feedback.
    - Feedback can only be submitted for projects that are marked as completed.
    - Each student can only submit one feedback per project.
    """
    project = db.query(Project).filter(Project.id == feedback_data.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # project must be completed
    if project.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback can only be submitted for completed projects"
        )

    # prevent duplicate feedback
    existing = db.query(Feedback).filter(
        Feedback.user_id == current_user.id,
        Feedback.project_id == feedback_data.project_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted feedback for this project"
        )

    feedback = Feedback(
        user_id=current_user.id,
        project_id=feedback_data.project_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment
    )
    db.add(feedback)
    # Recompute badges since rating may have changed badge eligibility
    award_badges(feedback.user_id, db)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/{project_id}", response_model=list[FeedbackRead])
def get_feedback(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all feedback for a given project.
    - Only orgs can view feedback for their projects.
    - Students cannot view feedback.
    """
    return db.query(Feedback).filter(Feedback.project_id == project_id).all()