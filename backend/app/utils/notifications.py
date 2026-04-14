from sqlalchemy.orm import Session
from app.models import Notification


def create_notification(db: Session, recipient_id: int, message: str) -> None:
    """
    Creates a notification record for the given recipient.

    Intentionally does NOT commit — the calling endpoint owns the
    transaction so that notification creation and the parent operation
    are atomic. If the parent rolls back, the notification rolls back too.
    """
    notification = Notification(
        recipient_id=recipient_id,
        message=message
    )
    db.add(notification)