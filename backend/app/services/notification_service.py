from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def create_notification(
    db: Session,
    title: str,
    message: str,
    recipient: Optional[str] = None,
    *,
    recipient_user_id: Optional[int] = None,
    notification_type: str = "SYSTEM",
    project_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    action_url: Optional[str] = None,
    deduplicate_unread: bool = False,
):
    """Create and store a Module 8 in-app notification.

    Other modules call this function when a real action occurs.  New metadata
    fields make notifications project-aware and provide a safe frontend route
    to the record that caused the alert.  Existing callers that only provide
    title/message/recipient continue to work.
    """

    resolved_recipient = str(recipient or "").strip()
    resolved_user_id = recipient_user_id

    # If a direct email was supplied, capture the matching user id as well.
    # This makes authorization stronger while preserving the existing
    # recipient column used by legacy data and UI code.
    if resolved_user_id is None and resolved_recipient and "@" in resolved_recipient:
        user = db.query(User).filter(User.email == resolved_recipient).first()
        if user:
            resolved_user_id = user.id

    if not resolved_recipient and resolved_user_id is not None:
        user = db.query(User).filter(User.id == resolved_user_id).first()
        if user:
            resolved_recipient = user.email

    if not resolved_recipient:
        resolved_recipient = "ADMIN"

    normalized_type = str(notification_type or "SYSTEM").strip().upper().replace(" ", "_")

    if deduplicate_unread:
        existing = (
            db.query(Notification)
            .filter(
                Notification.title == title,
                Notification.message == message,
                Notification.recipient == resolved_recipient,
                Notification.status.in_(["Unread", "unread", "UNREAD"]),
            )
            .first()
        )
        if existing:
            return existing

    notification = Notification(
        title=title,
        message=message,
        recipient=resolved_recipient,
        recipient_user_id=resolved_user_id,
        notification_type=normalized_type,
        project_id=project_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        action_url=action_url,
        status="Unread",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
