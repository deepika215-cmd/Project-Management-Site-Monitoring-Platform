from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.auth import get_current_user

from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.models.notification import Notification

from app.schemas.task_schema import TaskCreate, TaskResponse

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ============================================================
# CREATE TASK
# ============================================================

@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can create tasks"
        )

    project = (
        db.query(Project)
        .filter(Project.id == task_data.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot receive new tasks"
        )

    if (
        current_user.role == "MANAGER"
        and current_user.id != project.manager_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Manager can create tasks only for their own project"
        )

    assignee = (
        db.query(User)
        .filter(User.id == task_data.assigned_to)
        .first()
    )

    if not assignee:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if not assignee.is_active:
        raise HTTPException(
            status_code=400,
            detail="Assigned user is inactive"
        )

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        status=task_data.status,
        project_id=task_data.project_id,
        assigned_to=task_data.assigned_to
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # --------------------------------------------------------
    # TASK ASSIGNMENT NOTIFICATION
    # --------------------------------------------------------

    create_notification(
        db=db,
        title="Task Assigned",
        message=(
            f"You have been assigned task "
            f"'{new_task.title}' for Project "
            f"#{project.id} - {project.project_name}."
        ),
        recipient=assignee.email
    )

    return new_task


# ============================================================
# GET ALL ACCESSIBLE TASKS
# ============================================================

@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "ADMIN":
        return (
            db.query(Task)
            .order_by(Task.id.desc())
            .all()
        )

    if current_user.role == "MANAGER":
        return (
            db.query(Task)
            .join(Project, Task.project_id == Project.id)
            .filter(Project.manager_id == current_user.id)
            .order_by(Task.id.desc())
            .all()
        )

    return (
        db.query(Task)
        .filter(Task.assigned_to == current_user.id)
        .order_by(Task.id.desc())
        .all()
    )


# ============================================================
# GET MY TASKS
# ============================================================

@router.get("/my", response_model=list[TaskResponse])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Task)
        .filter(Task.assigned_to == current_user.id)
        .order_by(Task.id.desc())
        .all()
    )


# ============================================================
# TASK DEADLINE NOTIFICATIONS
# ============================================================

@router.get("/deadline-notifications")
def generate_task_deadline_notifications(
    db: Session = Depends(get_db)
):
    today = date.today()

    tasks = (
        db.query(Task)
        .filter(Task.due_date.isnot(None))
        .all()
    )

    upcoming_count = 0
    missed_count = 0
    notifications_created = 0

    for task in tasks:

        # ----------------------------------------------------
        # COMPLETED / CLOSED TASKS
        # ----------------------------------------------------

        if task.status in ["Completed", "Closed"]:
            continue

        days_remaining = (
            task.due_date - today
        ).days

        notification_title = None
        notification_message = None

        # ----------------------------------------------------
        # MISSED DEADLINE
        # ----------------------------------------------------

        if days_remaining < 0:

            notification_title = "Task Deadline Missed"

            notification_message = (
                f"Task #{task.id} - '{task.title}' "
                f"was due on {task.due_date} and "
                f"has not been completed."
            )

            missed_count += 1

        # ----------------------------------------------------
        # UPCOMING DEADLINE
        # ----------------------------------------------------

        elif days_remaining <= 7:

            notification_title = "Task Deadline Approaching"

            if days_remaining == 0:
                deadline_text = "today"

            elif days_remaining == 1:
                deadline_text = "tomorrow"

            else:
                deadline_text = (
                    f"in {days_remaining} days"
                )

            notification_message = (
                f"Task #{task.id} - '{task.title}' "
                f"is due {deadline_text} "
                f"on {task.due_date}."
            )

            upcoming_count += 1

        else:
            continue

        # ----------------------------------------------------
        # FIND ASSIGNED USER
        # ----------------------------------------------------

        assignee = (
            db.query(User)
            .filter(User.id == task.assigned_to)
            .first()
        )

        if not assignee:
            continue

        # ----------------------------------------------------
        # CORRECT DUPLICATE PREVENTION
        #
        # We identify the notification using:
        #   - notification type/title
        #   - task ID inside the message
        #   - recipient
        #
        # We intentionally DO NOT compare the complete message
        # because "in 2 days", "in 1 day", "tomorrow", etc.
        # changes as the date moves.
        # ----------------------------------------------------

        existing_notifications = (
            db.query(Notification)
            .filter(
                Notification.title == notification_title,
                Notification.recipient == assignee.email
            )
            .all()
        )

        task_identifier = f"Task #{task.id} -"

        duplicate_found = any(
            task_identifier in notification.message
            for notification in existing_notifications
        )

        if duplicate_found:
            continue

        # ----------------------------------------------------
        # CREATE NOTIFICATION
        # ----------------------------------------------------

        notification = Notification(
            title=notification_title,
            message=notification_message,
            recipient=assignee.email,
            status="Unread"
        )

        db.add(notification)

        notifications_created += 1

    db.commit()

    return {
        "message": (
            "Task deadline notifications "
            "processed successfully"
        ),
        "today": today,
        "upcoming_tasks": upcoming_count,
        "missed_tasks": missed_count,
        "notifications_created": notifications_created
    }


# ============================================================
# GET TASK BY ID
# ============================================================

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if current_user.role == "ADMIN":
        return task

    if current_user.role == "MANAGER":

        project = (
            db.query(Project)
            .filter(Project.id == task.project_id)
            .first()
        )

        if (
            not project
            or project.manager_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this task"
            )

        return task

    if task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this task"
        )

    return task


# ============================================================
# UPDATE TASK
# ============================================================

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    project = (
        db.query(Project)
        .filter(Project.id == task.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if current_user.role == "ADMIN":
        pass

    elif (
        current_user.role == "MANAGER"
        and project.manager_id == current_user.id
    ):
        pass

    elif task.assigned_to == current_user.id:
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update this task"
        )

    new_project = (
        db.query(Project)
        .filter(Project.id == task_data.project_id)
        .first()
    )

    if not new_project:
        raise HTTPException(
            status_code=404,
            detail="New project not found"
        )

    if new_project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot receive tasks"
        )

    new_assignee = (
        db.query(User)
        .filter(User.id == task_data.assigned_to)
        .first()
    )

    if not new_assignee:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if not new_assignee.is_active:
        raise HTTPException(
            status_code=400,
            detail="Assigned user is inactive"
        )

    old_assigned_to = task.assigned_to

    task.title = task_data.title
    task.description = task_data.description
    task.due_date = task_data.due_date
    task.status = task_data.status
    task.project_id = task_data.project_id
    task.assigned_to = task_data.assigned_to

    db.commit()
    db.refresh(task)

    # --------------------------------------------------------
    # NEW ASSIGNEE NOTIFICATION
    # --------------------------------------------------------

    if old_assigned_to != task.assigned_to:

        create_notification(
            db=db,
            title="Task Assigned",
            message=(
                f"You have been assigned task "
                f"'{task.title}' for Project "
                f"#{new_project.id} - "
                f"{new_project.project_name}."
            ),
            recipient=new_assignee.email
        )

    return task


# ============================================================
# DELETE TASK
# ============================================================

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    project = (
        db.query(Project)
        .filter(Project.id == task.project_id)
        .first()
    )

    if current_user.role == "ADMIN":
        pass

    elif (
        current_user.role == "MANAGER"
        and project
        and project.manager_id == current_user.id
    ):
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail=(
                "Only ADMIN or the Project Manager "
                "can delete this task"
            )
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }
