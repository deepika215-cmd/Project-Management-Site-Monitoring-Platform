from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.project_milestone import ProjectMilestone
from app.models.notification import Notification

from app.schemas.milestone_schema import (
    MilestoneCreate,
    MilestoneResponse
)


router = APIRouter(
    prefix="/milestones",
    tags=["Milestones"]
)


# ============================================================
# CREATE MILESTONE
# ============================================================

@router.post("/", response_model=MilestoneResponse)
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db)
):
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

@router.get("/", response_model=list[MilestoneResponse])
def get_milestones(
    db: Session = Depends(get_db)
):
    return db.query(ProjectMilestone).all()


# ============================================================
# GET MILESTONE BY ID
# ============================================================

@router.get("/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):
    milestone = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
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

@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db)
):
    milestone = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    # --------------------------------------------------------
    # Check whether milestone is being completed now
    # --------------------------------------------------------

    was_completed = milestone.status == "Completed"
    will_be_completed = milestone_data.status == "Completed"

    # Update milestone fields
    for key, value in milestone_data.model_dump().items():
        setattr(milestone, key, value)

    db.commit()
    db.refresh(milestone)

    # --------------------------------------------------------
    # Create notifications only when milestone becomes
    # Completed for the first time.
    # --------------------------------------------------------

    if will_be_completed and not was_completed:

        notification_message = (
            f"Milestone '{milestone.title}' has been completed "
            f"for Project {milestone.project_id}."
        )

        # Manager notification
        manager_notification = Notification(
            title="Milestone Completed",
            message=notification_message,
            recipient="MANAGER",
            status="Unread"
        )

        # Admin notification
        admin_notification = Notification(
            title="Milestone Completed",
            message=notification_message,
            recipient="ADMIN",
            status="Unread"
        )

        db.add(manager_notification)
        db.add(admin_notification)

        db.commit()

    return milestone


# ============================================================
# DELETE MILESTONE
# ============================================================

@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):
    milestone = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
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