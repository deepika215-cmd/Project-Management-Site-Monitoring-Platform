from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database.database import get_db
from app.core.permissions import normalize_role, role_required

from app.models.notification import Notification
from app.models.user import User
from app.models.project import Project
from app.models.maintenance import Maintenance
from app.models.procurement_request import ProcurementRequest

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
        role_required(["ADMIN", "PROJECT_MANAGER"])
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "CONTRACTOR",
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
                normalize_role(current_user.role),
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "CONTRACTOR",
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
                normalize_role(current_user.role),
                "ALL",
            ]),
            Notification.status.in_(["Unread", "unread", "UNREAD"]),
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "CONTRACTOR",
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
                normalize_role(current_user.role),
                "ALL",
            ]),
            Notification.status.in_(["Unread", "unread", "UNREAD"]),
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "CONTRACTOR",
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
                normalize_role(current_user.role),
                "ALL",
            ]),
            Notification.status.in_(["Unread", "unread", "UNREAD"]),
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
        role_required(["ADMIN", "PROJECT_MANAGER"])
    ),
):
    return (
        db.query(Notification)
        .order_by(Notification.id.desc())
        .all()
    )


# ============================================================
# GENERATE SYSTEM ALERTS — MODULE 8
# ============================================================

@router.post("/generate-system-alerts")
def generate_system_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN", "PROJECT_MANAGER"])),
):
    """Create de-duplicated deadline/workflow alerts from live database data."""
    today = date.today()
    created = 0

    def add_once(title: str, message: str, recipient: str):
        nonlocal created
        exists = db.query(Notification).filter(
            Notification.title == title,
            Notification.message == message,
            Notification.recipient == recipient,
            Notification.status.in_(["Unread", "unread", "UNREAD"]),
        ).first()
        if not exists:
            db.add(Notification(title=title, message=message, recipient=recipient, status="Unread"))
            created += 1

    projects = db.query(Project).all()
    for project in projects:
        if project.status in ["Completed", "Closed"] or not project.end_date:
            continue
        days = (project.end_date - today).days
        if days > 7:
            continue
        manager = db.query(User).filter(User.id == project.manager_id, User.is_active == True).first()
        recipient = manager.email if manager and manager.email else "ADMIN"
        if days < 0:
            title = "Project Deadline Missed"
            message = f"{project.project_name} passed its deadline on {project.end_date}."
        else:
            title = "Project Deadline Approaching"
            message = f"{project.project_name} is due on {project.end_date} ({days} day(s) remaining)."
        add_once(title, message, recipient)

    upcoming = db.query(Maintenance).filter(
        Maintenance.status != "Completed",
        Maintenance.scheduled_date >= today,
        Maintenance.scheduled_date <= today + timedelta(days=7),
    ).all()
    for item in upcoming:
        add_once(
            "Maintenance Due",
            f"Maintenance #{item.id} is scheduled for {item.scheduled_date}.",
            "PROJECT_MANAGER",
        )

    pending = db.query(ProcurementRequest).filter(
        ProcurementRequest.status.in_(["Pending", "PENDING", "Requested", "REQUESTED"])
    ).all()
    for req in pending:
        manager = None
        if req.project_id:
            project = db.query(Project).filter(Project.id == req.project_id).first()
            if project and project.manager_id:
                manager = db.query(User).filter(User.id == project.manager_id).first()
        recipient = manager.email if manager and manager.email else "PROJECT_MANAGER"
        add_once(
            "Procurement Approval Pending",
            f"Procurement request #{req.id} for {req.item_name} is awaiting approval.",
            recipient,
        )

    db.commit()
    return {"message": "System alerts generated", "created": created}


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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "CONTRACTOR",
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

    if normalize_role(current_user.role) not in ["ADMIN", "PROJECT_MANAGER"]:

        allowed_recipients = [
            current_user.email,
            current_user.name,
            current_user.role,
            normalize_role(current_user.role),
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
        role_required(["ADMIN", "PROJECT_MANAGER"])
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "CONTRACTOR",
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

    if normalize_role(current_user.role) not in ["ADMIN", "PROJECT_MANAGER"]:

        allowed_recipients = [
            current_user.email,
            current_user.name,
            current_user.role,
            normalize_role(current_user.role),
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
        role_required(["ADMIN", "PROJECT_MANAGER"])
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