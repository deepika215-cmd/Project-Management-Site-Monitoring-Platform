from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.project_milestone import ProjectMilestone
from app.schemas.milestone_schema import (
    MilestoneCreate,
    MilestoneResponse
)

router = APIRouter(
    prefix="/milestones",
    tags=["Milestones"]
)


# Create Milestone
@router.post("/", response_model=MilestoneResponse)
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db)
):
    new_milestone = ProjectMilestone(**milestone.dict())

    db.add(new_milestone)
    db.commit()
    db.refresh(new_milestone)

    return new_milestone


# Get All Milestones
@router.get("/", response_model=list[MilestoneResponse])
def get_milestones(
    db: Session = Depends(get_db)
):
    return db.query(ProjectMilestone).all()


# Get Milestone By ID
@router.get("/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):
    milestone = db.query(ProjectMilestone).filter(
        ProjectMilestone.id == milestone_id
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    return milestone


# Update Milestone
@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db)
):
    milestone = db.query(ProjectMilestone).filter(
        ProjectMilestone.id == milestone_id
    ).first()

    if not milestone:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found"
        )

    for key, value in milestone_data.dict().items():
        setattr(milestone, key, value)

    db.commit()
    db.refresh(milestone)

    return milestone


# Delete Milestone
@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):
    milestone = db.query(ProjectMilestone).filter(
        ProjectMilestone.id == milestone_id
    ).first()

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