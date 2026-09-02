from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.notification import Notification
from app.models.user import User

from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)


router = APIRouter(
    prefix="/notification",
    tags=["Notification"],
)


# ============================================================
# CREATE NOTIFICATION
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.post(
    "/",
    response_model=NotificationResponse
)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    ),
):
    new_notification = Notification(
        title=notification.title,
        message=notification.message,
        recipient=notification.recipient,
        status=notification.status,
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


# ============================================================
# GET MY NOTIFICATIONS
#
# The recipient field currently stores a string.
# We therefore use the logged-in user's email, name, or role
# as possible recipient values.
# ============================================================

@router.get(
    "/my",
    response_model=list[NotificationResponse]
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "CLIENT",
            "WORKER",
        ])
    ),
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.recipient.in_([
                current_user.email,
                current_user.name,
                current_user.role,
                "ALL",
            ])
        )
        .order_by(Notification.id.desc())
        .all()
    )

    return notifications


# ============================================================
# GET UNREAD MY NOTIFICATIONS
# ============================================================

@router.get(
    "/my/unread",
    response_model=list[NotificationResponse]
)
def get_my_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "CLIENT",
            "WORKER",
        ])
    ),
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.recipient.in_([
                current_user.email,
                current_user.name,
                current_user.role,
                "ALL",
            ]),
            Notification.status == "Unread",
        )
        .order_by(Notification.id.desc())
        .all()
    )

    return notifications


# ============================================================
# GET ALL NOTIFICATIONS
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    ),
):
    return (
        db.query(Notification)
        .order_by(Notification.id.desc())
        .all()
    )


# ============================================================
# GET NOTIFICATION BY ID
# ============================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "CLIENT",
            "WORKER",
        ])
    ),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    # Admin and Manager can access notifications.
    # Other users can only access their own notification.
    if current_user.role not in ["ADMIN", "MANAGER"]:
        allowed_recipients = [
            current_user.email,
            current_user.name,
            current_user.role,
            "ALL",
        ]

        if notification.recipient not in allowed_recipients:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this notification",
            )

    return notification


# ============================================================
# UPDATE NOTIFICATION
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.put(
    "/{notification_id}",
    response_model=NotificationResponse
)
def update_notification(
    notification_id: int,
    updated_notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    ),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    notification.title = updated_notification.title
    notification.message = updated_notification.message
    notification.recipient = updated_notification.recipient
    notification.status = updated_notification.status

    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK NOTIFICATION AS READ
#
# A user can mark their own notification as read.
# ADMIN/MANAGER can mark any notification as read.
# ============================================================

@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "CLIENT",
            "WORKER",
        ])
    ),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    # Non-admin/manager users can only mark
    # their own notifications as read.
    if current_user.role not in ["ADMIN", "MANAGER"]:
        allowed_recipients = [
            current_user.email,
            current_user.name,
            current_user.role,
            "ALL",
        ]

        if notification.recipient not in allowed_recipients:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this notification",
            )

    notification.status = "Read"

    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK ALL MY NOTIFICATIONS AS READ
# ============================================================

@router.put(
    "/my/read-all",
    response_model=dict
)
def mark_all_my_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "CLIENT",
            "WORKER",
        ])
    ),
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.recipient.in_([
                current_user.email,
                current_user.name,
                current_user.role,
                "ALL",
            ]),
            Notification.status == "Unread",
        )
        .all()
    )

    for notification in notifications:
        notification.status = "Read"

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications),
    }


# ============================================================
# DELETE NOTIFICATION
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.delete(
    "/{notification_id}"
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    ),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted successfully"
    }