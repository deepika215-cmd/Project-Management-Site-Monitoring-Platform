from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    title: str,
    message: str,
    recipient: str,
):
    """
    Create and store an in-app notification.

    This function is used by other modules whenever
    an important action occurs in the system.
    """

    notification = Notification(
        title=title,
        message=message,
        recipient=recipient,
        status="Unread",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification