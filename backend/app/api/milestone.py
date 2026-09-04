from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.project_milestone import ProjectMilestone
from app.models.notification import Notification
from app.models.project import Project
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.user import User

from app.schemas.milestone_schema import (
    MilestoneCreate,
    MilestoneResponse
)


router = APIRouter(
    prefix="/milestones",
    tags=["Milestones"]
)


# ============================================================
# HELPER: GET PROJECT USERS FOR NOTIFICATIONS
# ============================================================

def get_project_notification_recipients(
    db: Session,
    project_id: int
):
    """
    Get the email addresses of:
    - Project Manager
    - Assigned active Engineers

    These users are the relevant recipients for
    project-specific milestone notifications.
    """

    recipients = set()

    # --------------------------------------------------------
    # Get project
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return recipients

    # --------------------------------------------------------
    # Project Manager
    # --------------------------------------------------------

    if project.manager_id:

        manager = (
            db.query(User)
            .filter(
                User.id == project.manager_id,
                User.is_active == True
            )
            .first()
        )

        if manager:
            recipients.add(manager.email)

    # --------------------------------------------------------
    # Assigned Engineers
    # --------------------------------------------------------

    assignments = (
        db.query(ProjectEngineerAssignment)
        .filter(
            ProjectEngineerAssignment.project_id == project_id
        )
        .all()
    )

    for assignment in assignments:

        engineer = (
            db.query(User)
            .filter(
                User.id == assignment.engineer_id,
                User.role == "ENGINEER",
                User.is_active == True
            )
            .first()
        )

        if engineer:
            recipients.add(engineer.email)

    return recipients


# ============================================================
# CREATE MILESTONE
# ============================================================

@router.post(
    "/",
    response_model=MilestoneResponse
)
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Verify project exists
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == milestone.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Create milestone
    # --------------------------------------------------------

    new_milestone = ProjectMilestone(
        **milestone.model_dump()
    )

    db.add(new_milestone)
    db.commit()
    db.refresh(new_milestone)

    return new_milestone


# ============================================================
# GET ALL MILESTONES
# ============================================================

@router.get(
    "/",
    response_model=list[MilestoneResponse]
)
def get_milestones(
    db: Session = Depends(get_db)
):

    return (
        db.query(ProjectMilestone)
        .order_by(ProjectMilestone.id.desc())
        .all()
    )


# ============================================================
# DEADLINE NOTIFICATIONS
#
# IMPORTANT:
# This route MUST appear before:
#
# GET /{milestone_id}
#
# Otherwise FastAPI may try to parse
# "deadline-notifications" as an integer milestone_id.
# ============================================================

@router.get(
    "/deadline-notifications"
)
def generate_milestone_deadline_notifications(
    db: Session = Depends(get_db)
):

    today = date.today()

    # --------------------------------------------------------
    # Get all milestones
    # --------------------------------------------------------

    milestones = (
        db.query(ProjectMilestone)
        .all()
    )

    notifications_created = 0
    upcoming_count = 0
    missed_count = 0

    # --------------------------------------------------------
    # Process each milestone
    # --------------------------------------------------------

    for milestone in milestones:

        # ----------------------------------------------------
        # Ignore milestones without due date
        # ----------------------------------------------------

        if not milestone.due_date:
            continue

        # ----------------------------------------------------
        # Completed milestones do not need deadline alerts
        # ----------------------------------------------------

        if milestone.status == "Completed":
            continue

        # ----------------------------------------------------
        # Calculate days remaining
        # ----------------------------------------------------

        days_remaining = (
            milestone.due_date - today
        ).days

        notification_title = None
        notification_message = None

        # ====================================================
        # MISSED DEADLINE
        # ====================================================

        if days_remaining < 0:

            notification_title = "Milestone Deadline Missed"

            notification_message = (
                f"Milestone '{milestone.title}' for "
                f"Project {milestone.project_id} was due on "
                f"{milestone.due_date} and has not been completed."
            )

            missed_count += 1

        # ====================================================
        # UPCOMING DEADLINE
        # ====================================================

        elif days_remaining <= 7:

            notification_title = (
                "Milestone Deadline Approaching"
            )

            if days_remaining == 0:

                deadline_text = "today"

            elif days_remaining == 1:

                deadline_text = "tomorrow"

            else:

                deadline_text = (
                    f"in {days_remaining} days"
                )

            notification_message = (
                f"Milestone '{milestone.title}' for "
                f"Project {milestone.project_id} is due "
                f"{deadline_text} on {milestone.due_date}."
            )

            upcoming_count += 1

        # ----------------------------------------------------
        # More than 7 days away
        # ----------------------------------------------------

        else:
            continue

        # ====================================================
        # GET RELEVANT PROJECT USERS
        # ====================================================

        recipients = get_project_notification_recipients(
            db=db,
            project_id=milestone.project_id
        )

        # ====================================================
        # CREATE NOTIFICATIONS
        # ====================================================

        for recipient in recipients:

            # ------------------------------------------------
            # Duplicate prevention
            # ------------------------------------------------

            existing_notification = (
                db.query(Notification)
                .filter(
                    Notification.title == notification_title,
                    Notification.message == notification_message,
                    Notification.recipient == recipient
                )
                .first()
            )

            if existing_notification:
                continue

            notification = Notification(
                title=notification_title,
                message=notification_message,
                recipient=recipient,
                status="Unread"
            )

            db.add(notification)

            notifications_created += 1

    # --------------------------------------------------------
    # Save notifications
    # --------------------------------------------------------

    db.commit()

    return {
        "message": (
            "Milestone deadline notifications "
            "processed successfully"
        ),
        "today": today,
        "upcoming_milestones": upcoming_count,
        "missed_milestones": missed_count,
        "notifications_created": notifications_created
    }


# ============================================================
# GET MILESTONE BY ID
# ============================================================

@router.get(
    "/{milestone_id}",
    response_model=MilestoneResponse
)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):

    milestone = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.id == milestone_id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    return milestone


# ============================================================
# UPDATE MILESTONE
#
# Automatically creates notifications when milestone
# status changes to "Completed".
# ============================================================

@router.put(
    "/{milestone_id}",
    response_model=MilestoneResponse
)
def update_milestone(
    milestone_id: int,
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find milestone
    # --------------------------------------------------------

    milestone = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.id == milestone_id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    # --------------------------------------------------------
    # Check completion transition
    # --------------------------------------------------------

    was_completed = (
        milestone.status == "Completed"
    )

    will_be_completed = (
        milestone_data.status == "Completed"
    )

    # --------------------------------------------------------
    # Update milestone
    # --------------------------------------------------------

    for key, value in milestone_data.model_dump().items():
        setattr(milestone, key, value)

    db.commit()
    db.refresh(milestone)

    # ========================================================
    # MILESTONE COMPLETED NOTIFICATION
    # ========================================================

    if will_be_completed and not was_completed:

        notification_message = (
            f"Milestone '{milestone.title}' has been completed "
            f"for Project {milestone.project_id}."
        )

        # ----------------------------------------------------
        # Get project manager + assigned engineers
        # ----------------------------------------------------

        recipients = get_project_notification_recipients(
            db=db,
            project_id=milestone.project_id
        )

        # ----------------------------------------------------
        # Notify each relevant user
        # ----------------------------------------------------

        for recipient in recipients:

            notification = Notification(
                title="Milestone Completed",
                message=notification_message,
                recipient=recipient,
                status="Unread"
            )

            db.add(notification)

        db.commit()

    return milestone


# ============================================================
# DELETE MILESTONE
# ============================================================

@router.delete(
    "/{milestone_id}"
)
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):

    milestone = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.id == milestone_id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    db.delete(milestone)
    db.commit()

    return {
        "message": "Milestone deleted successfully"
    }
