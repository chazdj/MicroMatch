from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Notification, User
from app.schemas.notification import NotificationRead
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationRead], status_code=status.HTTP_200_OK)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all notifications for the authenticated user.

    Business Rules:
    - Any authenticated user may access this endpoint (student or organization).
    - Returns only notifications belonging to the current user.
    - Results ordered newest-first.
    - Returns empty list if no notifications exist — not a 404.

    Raises:
    - 401 if no valid JWT token provided
    """

    notifications = (
        db.query(Notification)
        .filter(Notification.recipient_id == current_user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())        .all()
    )

    return notifications


@router.put("/{notification_id}/read", response_model=NotificationRead, status_code=status.HTTP_200_OK)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marks a specific notification as read (is_read = True).

    Business Rules:
    - Any authenticated user may access this endpoint.
    - User may only mark their own notifications as read.
    - Marking an already-read notification as read is a no-op (returns 200, no error).

    Raises:
    - 401 if no valid JWT token provided
    - 404 if notification does not exist
    - 403 if notification belongs to a different user
    """

    # ---------------------------------------------------------
    # Validate notification exists
    # ---------------------------------------------------------
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # ---------------------------------------------------------
    # Enforce ownership — user can only mark their own as read
    # ---------------------------------------------------------
    if notification.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification"
        )

    # ---------------------------------------------------------
    # Mark as read (idempotent — no error if already read)
    # ---------------------------------------------------------
    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification