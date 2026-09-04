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
# Users can only see notifications addressed to:
# - their email
# - their name
# - their role
# - ALL
#
# Allowed roles:
# ADMIN, MANAGER, ENGINEER, CLIENT, WORKER
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
# GET MY UNREAD NOTIFICATIONS
#
# Allowed roles:
# ADMIN, MANAGER, ENGINEER, CLIENT, WORKER
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
# GET MY UNREAD NOTIFICATION COUNT
#
# Allowed roles:
# ADMIN, MANAGER, ENGINEER, CLIENT, WORKER
# ============================================================

@router.get(
    "/my/unread/count",
    response_model=dict
)
def get_my_unread_notification_count(
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
    count = (
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
        .count()
    )

    return {
        "unread_count": count
    }


# ============================================================
# MARK ALL MY NOTIFICATIONS AS READ
#
# Allowed roles:
# ADMIN, MANAGER, ENGINEER, CLIENT, WORKER
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
#
# ADMIN/MANAGER:
#     Can access any notification.
#
# ENGINEER/CLIENT/WORKER:
#     Can access only their own notification.
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

    # --------------------------------------------------------
    # ADMIN and MANAGER can access any notification
    # --------------------------------------------------------

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
# ADMIN/MANAGER:
#     Can mark any notification as read.
#
# ENGINEER/CLIENT/WORKER:
#     Can mark only their own notification as read.
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

    # --------------------------------------------------------
    # Non-admin/manager users can only mark their own
    # notifications as read.
    # --------------------------------------------------------

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