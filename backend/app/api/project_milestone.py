from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.project import Project

from app.database.database import get_db
from app.models.project_milestone import ProjectMilestone
from app.schemas.project_milestone_schema import (
    ProjectMilestoneCreate,
    ProjectMilestoneResponse,
)

router = APIRouter(
    prefix="/milestones",
    tags=["Milestones"],
)


# GET ALL MILESTONES
@router.get("/", response_model=list[ProjectMilestoneResponse])
def get_all_milestones(db: Session = Depends(get_db)):
    return db.query(ProjectMilestone).all()


# GET MILESTONE BY ID
@router.get("/{milestone_id}", response_model=ProjectMilestoneResponse)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
):
    milestone = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
        .first()
    )

    if milestone is None:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found",
        )

    return milestone


# CREATE MILESTONE
@router.post("/", response_model=ProjectMilestoneResponse)
def create_milestone(
    milestone: ProjectMilestoneCreate,
    db: Session = Depends(get_db),
):
    # Check whether project exists
    project = db.query(Project).filter(
        Project.id == milestone.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    new_milestone = ProjectMilestone(
        **milestone.model_dump()
    )

    db.add(new_milestone)
    db.commit()
    db.refresh(new_milestone)

    return new_milestone

# UPDATE MILESTONE
@router.put("/{milestone_id}", response_model=ProjectMilestoneResponse)
def update_milestone(
    milestone_id: int,
    updated_milestone: ProjectMilestoneCreate,
    db: Session = Depends(get_db),
):
    milestone = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
        .first()
    )

    if milestone is None:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found",
        )

    for key, value in updated_milestone.model_dump().items():
        setattr(milestone, key, value)

    db.commit()
    db.refresh(milestone)

    return milestone


# DELETE MILESTONE
@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
):
    milestone = (
        db.query(ProjectMilestone)
        .filter(ProjectMilestone.id == milestone_id)
        .first()
    )

    if milestone is None:
        raise HTTPException(
            status_code=404,
            detail="Milestone not found",
        )

    db.delete(milestone)
    db.commit()

    return {
        "message": "Milestone deleted successfully"
    }