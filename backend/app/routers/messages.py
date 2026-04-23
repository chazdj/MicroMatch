from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import *
from app.schemas.message import MessageCreate, MessageRead
from app.core.dependencies import require_project_participant
from app.utils.notifications import create_notification

router = APIRouter(prefix="/projects", tags=["Messages"])

def _get_recipient_id(db: Session, project_id: int, sender_id: int) -> int | None:
    """
    Returns the other participant's user_id for notification purposes.
    - If sender is the org → notify the accepted student
    - If sender is a student → notify the org
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    if project.organization_id == sender_id:
        # Sender is org → find the accepted student
        app = (
            db.query(Application)
            .filter(
                Application.project_id == project_id,
                Application.status == "accepted",
            )
            .first()
        )
        return app.student_id if app else None
    else:
        # Sender is student → notify org
        return project.organization_id

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

    # Notify the other participant
    recipient_id = _get_recipient_id(db, project_id, current_user.id)
    if recipient_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        preview = message_data.content[:60] + ("…" if len(message_data.content) > 60 else "")
        create_notification(
            db,
            recipient_id=recipient_id,
            message=f"💬 New message in '{project.title}': {preview}",
        )

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