from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ProjectMessage, User
from app.schemas.message import MessageCreate, MessageRead
from app.core.dependencies import require_project_participant

router = APIRouter(prefix="/projects", tags=["Messages"])


@router.post(
    "/{project_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED
)
def send_message(
    project_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_participant)
):
    """
    Send a message within a project.

    Business Rules:
    - Caller must be the owning organization OR the accepted student.
    - Message is scoped to the project.
    - Persists sender, content, and timestamp.

    Raises:
    - 404 if project not found
    - 403 if caller is not a project participant
    """
    message = ProjectMessage(
        project_id=project_id,
        sender_id=current_user.id,
        content=message_data.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get(
    "/{project_id}/messages",
    response_model=List[MessageRead]
)
def get_messages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_participant)
):
    """
    Retrieve the conversation history for a project.

    Business Rules:
    - Caller must be the owning organization OR the accepted student.
    - Returns messages ordered oldest → newest.

    Raises:
    - 404 if project not found
    - 403 if caller is not a project participant
    """
    messages = (
        db.query(ProjectMessage)
        .filter(ProjectMessage.project_id == project_id)
        .order_by(ProjectMessage.created_at.asc())
        .all()
    )
    return messages