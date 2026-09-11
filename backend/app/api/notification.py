from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import normalize_role, role_required

from app.models.notification import Notification
from app.models.user import User
from app.models.project import Project
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.task import Task
from app.models.project_milestone import ProjectMilestone
from app.models.procurement_request import ProcurementRequest
from app.models.attendance import Attendance
from app.models.worker import Worker
from app.models.worker_assignment import WorkerAssignment
from app.models.contractor import Contractor
from app.models.maintenance import Maintenance
from app.models.machinery import Machinery
from app.models.resource import Resource

from app.schemas.notification_schema import NotificationCreate, NotificationResponse


router = APIRouter(prefix="/notification", tags=["Notification"])

ALL_NOTIFICATION_ROLES = [
    "ADMIN",
    "PROJECT_MANAGER",
    "SITE_ENGINEER",
    "CONTRACTOR",
    "CLIENT",
    "WORKER",
]


# ============================================================
# MODULE 8 ACCESS HELPERS
# ============================================================

def _recipient_values_for_user(user: User) -> set[str]:
    """Recipient values that explicitly target the authenticated user.

    `ALL` is deliberately not included here.  Global notifications are handled
    separately so project-specific data cannot accidentally leak to unrelated
    users.
    """
    role = normalize_role(getattr(user, "role", None))
    values = {
        str(getattr(user, "email", "") or "").strip(),
        str(getattr(user, "role", "") or "").strip(),
        role,
    }
    if role == "PROJECT_MANAGER":
        values.update({"MANAGER", "PM", "PROJECT MANAGER"})
    if role == "SITE_ENGINEER":
        values.update({"ENGINEER", "SITE ENGINEER"})
    return {value for value in values if value}


def _directly_targets_user(notification: Notification, user: User) -> bool:
    if notification.recipient_user_id is not None:
        return notification.recipient_user_id == user.id
    recipient = str(notification.recipient or "").strip()
    return recipient in _recipient_values_for_user(user)


def _accessible_project_ids(db: Session, user: User) -> set[int]:
    """Projects represented by the current BuildTrack assignment tables."""
    role = normalize_role(getattr(user, "role", None))

    if role == "ADMIN":
        return {row[0] for row in db.query(Project.id).all()}

    if role == "PROJECT_MANAGER":
        return {
            row[0]
            for row in db.query(Project.id).filter(Project.manager_id == user.id).all()
        }

    if role == "SITE_ENGINEER":
        return {
            row[0]
            for row in db.query(ProjectEngineerAssignment.project_id)
            .filter(ProjectEngineerAssignment.engineer_id == user.id)
            .all()
        }

    if role == "CONTRACTOR":
        contractor_ids: set[int] = set()
        project_ids: set[int] = set()
        email = str(getattr(user, "email", "") or "").strip()
        if email:
            contractors = db.query(Contractor).filter(Contractor.email == email).all()
            for contractor in contractors:
                contractor_ids.add(contractor.id)
                if contractor.project_id:
                    project_ids.add(contractor.project_id)
        if contractor_ids:
            project_ids.update(
                row[0]
                for row in db.query(WorkerAssignment.project_id)
                .filter(WorkerAssignment.contractor_id.in_(contractor_ids))
                .all()
            )
        return project_ids

    if role == "WORKER":
        email = str(getattr(user, "email", "") or "").strip()
        if not email:
            return set()
        workers = db.query(Worker).filter(Worker.email == email).all()
        worker_ids = [worker.id for worker in workers]
        if not worker_ids:
            return set()
        return {
            row[0]
            for row in db.query(WorkerAssignment.project_id)
            .filter(WorkerAssignment.worker_id.in_(worker_ids))
            .all()
        }

    # There is no dedicated client-project assignment table in the current
    # project schema.  Client project notifications must therefore be sent to
    # a specific client email/user id instead of the broad CLIENT role.
    return set()


def _can_view_notification(db: Session, notification: Notification, user: User) -> bool:
    role = normalize_role(getattr(user, "role", None))
    if role == "ADMIN":
        return True

    recipient = str(notification.recipient or "").strip()
    direct = _directly_targets_user(notification, user)

    if recipient.upper() == "ALL":
        # Global system notices can be seen by every authenticated role, but a
        # project-specific ALL notification still requires project access.
        if notification.project_id is None:
            return str(notification.notification_type or "SYSTEM").upper() == "SYSTEM"
        return notification.project_id in _accessible_project_ids(db, user)

    if not direct:
        return False

    if notification.project_id is None:
        return True

    # A direct user id/email is considered an explicit project responsibility
    # for this notification.  Role-wide recipients must match an assignment.
    recipient_is_direct_identity = (
        notification.recipient_user_id == user.id
        or recipient == str(getattr(user, "email", "") or "").strip()
    )
    if recipient_is_direct_identity:
        return True

    return notification.project_id in _accessible_project_ids(db, user)


def _visible_notifications(db: Session, user: User, unread_only: bool = False) -> list[Notification]:
    query = db.query(Notification)
    if unread_only:
        query = query.filter(Notification.status.in_(["Unread", "unread", "UNREAD"]))
    rows = query.order_by(Notification.id.desc()).all()
    return [row for row in rows if _can_view_notification(db, row, user)]


def _active_user(db: Session, user_id: int | None) -> User | None:
    if not user_id:
        return None
    return (
        db.query(User)
        .filter(User.id == user_id, User.is_active == True)
        .first()
    )


def _project_staff(db: Session, project_id: int) -> list[User]:
    """Manager + assigned engineers for a project, de-duplicated by id."""
    users: dict[int, User] = {}
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return []

    manager = _active_user(db, project.manager_id)
    if manager:
        users[manager.id] = manager

    engineer_ids = [
        row[0]
        for row in db.query(ProjectEngineerAssignment.engineer_id)
        .filter(ProjectEngineerAssignment.project_id == project_id)
        .all()
    ]
    if engineer_ids:
        for engineer in (
            db.query(User)
            .filter(User.id.in_(engineer_ids), User.is_active == True)
            .all()
        ):
            users[engineer.id] = engineer

    return list(users.values())


def _contractor_users_for_project(db: Session, project_id: int) -> list[User]:
    emails: set[str] = set()
    contractors = db.query(Contractor).filter(Contractor.project_id == project_id).all()
    contractor_ids = {contractor.id for contractor in contractors}

    # Worker assignments can also link a contractor to the project even if the
    # contractor.project_id field is not populated.
    contractor_ids.update(
        row[0]
        for row in db.query(WorkerAssignment.contractor_id)
        .filter(WorkerAssignment.project_id == project_id)
        .all()
    )
    if contractor_ids:
        for contractor in db.query(Contractor).filter(Contractor.id.in_(contractor_ids)).all():
            if contractor.email:
                emails.add(contractor.email)

    if not emails:
        return []
    return (
        db.query(User)
        .filter(User.email.in_(emails), User.is_active == True)
        .all()
    )


def _attendance_alert_users(db: Session, project_id: int, worker_id: int) -> list[User]:
    """Users responsible for an attendance exception: PM + assigned contractor."""
    users: dict[int, User] = {}
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        manager = _active_user(db, project.manager_id)
        if manager:
            users[manager.id] = manager

    assignment = (
        db.query(WorkerAssignment)
        .filter(
            WorkerAssignment.worker_id == worker_id,
            WorkerAssignment.project_id == project_id,
            WorkerAssignment.assignment_status == "ACTIVE",
        )
        .order_by(WorkerAssignment.id.desc())
        .first()
    )
    if assignment:
        contractor = db.query(Contractor).filter(Contractor.id == assignment.contractor_id).first()
        if contractor and contractor.email:
            contractor_user = db.query(User).filter(
                User.email == contractor.email,
                User.is_active == True,
            ).first()
            if contractor_user:
                users[contractor_user.id] = contractor_user

    return list(users.values())


def _action_for_user(user: User, project_id: int | None, preferred: str | None = None) -> str | None:
    if preferred:
        return preferred
    role = normalize_role(getattr(user, "role", None))
    if project_id and role in {"ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "CLIENT"}:
        return f"/projects/project-details/{project_id}"
    if role == "WORKER":
        return "/worker-dashboard"
    return "/notifications"


# ============================================================
# CREATE / READ / UPDATE / DELETE
# ============================================================

@router.post("/", response_model=NotificationResponse)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"])),
):
    if notification.recipient_user_id is not None:
        recipient_user = db.query(User).filter(User.id == notification.recipient_user_id).first()
        if not recipient_user:
            raise HTTPException(status_code=404, detail="Recipient user not found")

    row = Notification(**notification.model_dump())
    if str(row.status or "").lower() == "read":
        row.read_at = datetime.utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/my", response_model=list[NotificationResponse])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(ALL_NOTIFICATION_ROLES)),
):
    return _visible_notifications(db, current_user)


@router.get("/my/unread", response_model=list[NotificationResponse])
def get_my_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(ALL_NOTIFICATION_ROLES)),
):
    return _visible_notifications(db, current_user, unread_only=True)


@router.get("/my/unread/count", response_model=dict)
def get_my_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(ALL_NOTIFICATION_ROLES)),
):
    return {"unread_count": len(_visible_notifications(db, current_user, unread_only=True))}


@router.put("/my/read-all", response_model=dict)
def mark_all_my_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(ALL_NOTIFICATION_ROLES)),
):
    rows = _visible_notifications(db, current_user, unread_only=True)
    now = datetime.utcnow()
    for row in rows:
        row.status = "Read"
        row.read_at = now
    db.commit()
    return {"message": "All notifications marked as read", "updated_count": len(rows)}


@router.get("/", response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"])),
):
    """Admin notification management feed.

    Project managers use /notification/my so they cannot browse notifications
    belonging to unrelated projects or users.
    """
    return db.query(Notification).order_by(Notification.id.desc()).all()


@router.put("/read-all", response_model=dict)
def mark_all_notifications_as_read_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"])),
):
    """Admin management action: mark the organization notification feed read."""
    rows = db.query(Notification).filter(
        Notification.status.in_(["Unread", "unread", "UNREAD"])
    ).all()
    now = datetime.utcnow()
    for row in rows:
        row.status = "Read"
        row.read_at = now
    db.commit()
    return {"message": "All notifications marked as read", "updated_count": len(rows)}


# ============================================================
# GENERATE ALERTS — ADMIN BUTTON / LIVE DATABASE SCAN
# ============================================================

@router.post("/generate-system-alerts")
def generate_system_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"])),
):
    """Generate de-duplicated Module 8 alerts from current database data.

    This complements event-driven notifications.  It is especially useful for
    time-based conditions (deadlines, pending approvals and maintenance) that
    can become important even when nobody is editing the corresponding module.
    """
    today = date.today()
    created = 0
    by_type: dict[str, int] = {
        "DEADLINE": 0,
        "PROCUREMENT": 0,
        "ATTENDANCE": 0,
        "MAINTENANCE": 0,
        "SYSTEM": 0,
    }

    def add_once(
        *,
        title: str,
        message: str,
        user: User,
        notification_type: str,
        project_id: int | None = None,
        related_entity_type: str | None = None,
        related_entity_id: int | None = None,
        action_url: str | None = None,
    ) -> bool:
        nonlocal created
        existing = (
            db.query(Notification)
            .filter(
                Notification.title == title,
                Notification.message == message,
                Notification.recipient_user_id == user.id,
                Notification.status.in_(["Unread", "unread", "UNREAD"]),
            )
            .first()
        )
        if existing:
            return False

        kind = notification_type.upper()
        db.add(
            Notification(
                title=title,
                message=message,
                recipient=user.email,
                recipient_user_id=user.id,
                notification_type=kind,
                project_id=project_id,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                action_url=action_url or _action_for_user(user, project_id),
                status="Unread",
            )
        )
        # SessionLocal disables autoflush, so flush here to make the new row
        # visible to duplicate checks later in the same scan.
        db.flush()
        created += 1
        by_type[kind] = by_type.get(kind, 0) + 1
        return True

    # 1) Project deadlines — responsible project manager.
    projects = db.query(Project).all()
    for project in projects:
        if str(project.status or "").strip().upper() in {"COMPLETED", "CLOSED"} or not project.end_date:
            continue
        days = (project.end_date - today).days
        if days > 7:
            continue
        manager = _active_user(db, project.manager_id)
        if not manager:
            continue
        if days < 0:
            title = "Project Deadline Missed"
            message = f"{project.project_name} passed its deadline on {project.end_date}."
        elif days == 0:
            title = "Project Due Today"
            message = f"{project.project_name} is due today ({project.end_date})."
        else:
            title = "Project Deadline Approaching"
            message = f"{project.project_name} is due on {project.end_date} ({days} day(s) remaining)."
        add_once(
            title=title,
            message=message,
            user=manager,
            notification_type="DEADLINE",
            project_id=project.id,
            related_entity_type="PROJECT",
            related_entity_id=project.id,
        )

    # 2) Milestone deadlines — project manager + assigned site engineers.
    milestones = db.query(ProjectMilestone).filter(ProjectMilestone.due_date.isnot(None)).all()
    for milestone in milestones:
        if str(milestone.status or "").strip().upper() in {"COMPLETED", "CLOSED", "DONE"}:
            continue
        days = (milestone.due_date - today).days
        if days > 7:
            continue
        project = db.query(Project).filter(Project.id == milestone.project_id).first()
        project_name = project.project_name if project else f"Project #{milestone.project_id}"
        if days < 0:
            title = "Milestone Deadline Missed"
            message = f"Milestone '{milestone.title}' for {project_name} was due on {milestone.due_date}."
        elif days == 0:
            title = "Milestone Due Today"
            message = f"Milestone '{milestone.title}' for {project_name} is due today."
        else:
            title = "Milestone Deadline Approaching"
            message = f"Milestone '{milestone.title}' for {project_name} is due in {days} day(s)."
        for user in _project_staff(db, milestone.project_id):
            add_once(
                title=title,
                message=message,
                user=user,
                notification_type="DEADLINE",
                project_id=milestone.project_id,
                related_entity_type="MILESTONE",
                related_entity_id=milestone.id,
            )

    # 3) Task deadlines — only the assigned user.
    tasks = db.query(Task).filter(Task.due_date.isnot(None)).all()
    for task in tasks:
        if str(task.status or "").strip().upper() in {"COMPLETED", "CLOSED", "DONE"}:
            continue
        days = (task.due_date - today).days
        if days > 7:
            continue
        assignee = _active_user(db, task.assigned_to)
        if not assignee:
            continue
        project = db.query(Project).filter(Project.id == task.project_id).first()
        project_name = project.project_name if project else f"Project #{task.project_id}"
        if days < 0:
            title = "Task Deadline Missed"
            message = f"Task '{task.title}' for {project_name} was due on {task.due_date}."
        elif days == 0:
            title = "Task Due Today"
            message = f"Task '{task.title}' for {project_name} is due today."
        else:
            title = "Task Deadline Approaching"
            message = f"Task '{task.title}' for {project_name} is due in {days} day(s)."
        add_once(
            title=title,
            message=message,
            user=assignee,
            notification_type="DEADLINE",
            project_id=task.project_id,
            related_entity_type="TASK",
            related_entity_id=task.id,
            action_url=_action_for_user(assignee, task.project_id),
        )

    # 4) Procurement alerts — responsible project manager.
    pending_requests = (
        db.query(ProcurementRequest)
        .filter(ProcurementRequest.status.in_(["Pending", "PENDING", "Requested", "REQUESTED"]))
        .all()
    )
    for req in pending_requests:
        project = db.query(Project).filter(Project.id == req.project_id).first()
        manager = _active_user(db, project.manager_id if project else None)
        if not manager:
            continue
        urgency = ""
        if req.required_date:
            days = (req.required_date - today).days
            if days < 0:
                urgency = f" Required date {req.required_date} has passed."
            elif days <= 3:
                urgency = f" Required by {req.required_date} ({days} day(s) remaining)."
        add_once(
            title="Procurement Action Required",
            message=f"Procurement request #{req.id} for {req.item_name} is awaiting approval.{urgency}",
            user=manager,
            notification_type="PROCUREMENT",
            project_id=req.project_id,
            related_entity_type="PROCUREMENT_REQUEST",
            related_entity_id=req.id,
            action_url="/procurement",
        )

    # 5) Attendance alerts — actual today's non-present attendance data.
    today_text = today.isoformat()
    attendance_rows = db.query(Attendance).filter(Attendance.date == today_text).all()
    for attendance in attendance_rows:
        status = str(attendance.status or "").strip().upper()
        if status in {"PRESENT", "ON TIME", "ONTIME"}:
            continue
        worker = db.query(Worker).filter(Worker.id == attendance.worker_id).first()
        worker_name = worker.name if worker else f"Worker #{attendance.worker_id}"
        project_id = attendance.project_id
        if not project_id and worker:
            assignment = (
                db.query(WorkerAssignment)
                .filter(WorkerAssignment.worker_id == worker.id)
                .order_by(WorkerAssignment.id.desc())
                .first()
            )
            project_id = assignment.project_id if assignment else None
        if not project_id:
            continue
        for user in _attendance_alert_users(db, project_id, attendance.worker_id):
            add_once(
                title="Attendance Alert",
                message=f"{worker_name} is marked {attendance.status} for {today_text} in Project #{project_id}.",
                user=user,
                notification_type="ATTENDANCE",
                project_id=project_id,
                related_entity_type="ATTENDANCE",
                related_entity_id=attendance.id,
                action_url="/attendance",
            )

    # 6) Maintenance alerts — project staff responsible for the machinery.
    upcoming_maintenance = (
        db.query(Maintenance)
        .filter(
            Maintenance.status != "Completed",
            Maintenance.scheduled_date >= today,
            Maintenance.scheduled_date <= today + timedelta(days=7),
        )
        .all()
    )
    for item in upcoming_maintenance:
        machinery = db.query(Machinery).filter(Machinery.id == item.machinery_id).first()
        project_id = machinery.project_id if machinery else None
        if not project_id:
            continue
        equipment_name = machinery.name if machinery else f"Machinery #{item.machinery_id}"
        for user in _project_staff(db, project_id):
            add_once(
                title="Maintenance Due",
                message=f"{equipment_name} has {item.maintenance_type} scheduled for {item.scheduled_date}.",
                user=user,
                notification_type="MAINTENANCE",
                project_id=project_id,
                related_entity_type="MAINTENANCE",
                related_entity_id=item.id,
                action_url="/resources/operations",
            )

    # 7) System/resource alerts — live resource state, not static cards.
    problem_resources = (
        db.query(Resource)
        .filter(Resource.status.in_(["Out of Service", "OUT OF SERVICE", "Unavailable", "UNAVAILABLE", "Maintenance", "MAINTENANCE"]))
        .all()
    )
    for resource in problem_resources:
        if not resource.project_id:
            continue
        for user in _project_staff(db, resource.project_id):
            add_once(
                title="Resource System Alert",
                message=f"{resource.name} is currently marked '{resource.status}' for Project #{resource.project_id}.",
                user=user,
                notification_type="SYSTEM",
                project_id=resource.project_id,
                related_entity_type="RESOURCE",
                related_entity_id=resource.id,
                action_url="/resources/operations",
            )

    db.commit()
    return {
        "message": f"Alert scan complete. {created} new notification(s) generated from live project data.",
        "created": created,
        "by_type": by_type,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(ALL_NOTIFICATION_ROLES)),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not _can_view_notification(db, notification, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this notification")
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    updated_notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"])),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in updated_notification.model_dump().items():
        setattr(notification, key, value)
    if str(notification.status or "").lower() == "read" and notification.read_at is None:
        notification.read_at = datetime.utcnow()
    elif str(notification.status or "").lower() != "read":
        notification.read_at = None

    db.commit()
    db.refresh(notification)
    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(ALL_NOTIFICATION_ROLES)),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not _can_view_notification(db, notification, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this notification")

    notification.status = "Read"
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"])),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}
