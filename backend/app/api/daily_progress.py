from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.daily_progress import DailyProgress
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.schemas.daily_progress_schema import (
    DailyProgressCreate,
    DailyProgressResponse,
)

router = APIRouter(
    prefix="/daily-progress",
    tags=["Daily Progress"],
)


# CREATE DAILY PROGRESS
@router.post("/", response_model=DailyProgressResponse)
def create_daily_progress(
    progress: DailyProgressCreate,
    db: Session = Depends(get_db),
):

    # 1. Check whether project exists
    project = db.query(Project).filter(
        Project.id == progress.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # 2. Check milestone if provided
    if progress.milestone_id is not None:

        milestone = db.query(ProjectMilestone).filter(
            ProjectMilestone.id == progress.milestone_id
        ).first()

        if milestone is None:
            raise HTTPException(
                status_code=404,
                detail="Milestone not found"
            )

        # Make sure milestone belongs to the same project
        if milestone.project_id != progress.project_id:
            raise HTTPException(
                status_code=400,
                detail="Milestone does not belong to this project"
            )

    # 3. Validate completion percentage
    if not 0 <= progress.completion_percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Completion percentage must be between 0 and 100"
        )

    # 4. Create daily progress record
    new_progress = DailyProgress(
        **progress.model_dump()
    )

    db.add(new_progress)

    # 5. Update project completion percentage
    project.completion_percentage = progress.completion_percentage

    db.commit()
    db.refresh(new_progress)

    return new_progress


# GET ALL DAILY PROGRESS
@router.get("/", response_model=list[DailyProgressResponse])
def get_all_daily_progress(
    db: Session = Depends(get_db)
):
    return db.query(DailyProgress).all()


# GET DAILY PROGRESS BY ID
@router.get("/{progress_id}", response_model=DailyProgressResponse)
def get_daily_progress_by_id(
    progress_id: int,
    db: Session = Depends(get_db),
):

    progress = db.query(DailyProgress).filter(
        DailyProgress.id == progress_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    return progress


# UPDATE DAILY PROGRESS
@router.put("/{progress_id}", response_model=DailyProgressResponse)
def update_daily_progress(
    progress_id: int,
    updated_progress: DailyProgressCreate,
    db: Session = Depends(get_db),
):

    progress = db.query(DailyProgress).filter(
        DailyProgress.id == progress_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    # Check project
    project = db.query(Project).filter(
        Project.id == updated_progress.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Check milestone
    if updated_progress.milestone_id is not None:

        milestone = db.query(ProjectMilestone).filter(
            ProjectMilestone.id == updated_progress.milestone_id
        ).first()

        if milestone is None:
            raise HTTPException(
                status_code=404,
                detail="Milestone not found"
            )

        if milestone.project_id != updated_progress.project_id:
            raise HTTPException(
                status_code=400,
                detail="Milestone does not belong to this project"
            )

    # Validate percentage
    if not 0 <= updated_progress.completion_percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Completion percentage must be between 0 and 100"
        )

    # Update fields
    for key, value in updated_progress.model_dump().items():
        setattr(progress, key, value)

    # Update project completion
    project.completion_percentage = (
        updated_progress.completion_percentage
    )

    db.commit()
    db.refresh(progress)

    return progress


# DELETE DAILY PROGRESS
@router.delete("/{progress_id}")
def delete_daily_progress(
    progress_id: int,
    db: Session = Depends(get_db),
):

    progress = db.query(DailyProgress).filter(
        DailyProgress.id == progress_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    db.delete(progress)
    db.commit()

    return {
        "message": "Daily Progress deleted successfully"
    }