from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.project import Project

from app.database.database import get_db
from app.models.weekly_progress import WeeklyProgress
from app.schemas.weekly_progress_schema import (
    WeeklyProgressCreate,
    WeeklyProgressResponse,
)

router = APIRouter(
    prefix="/weekly-progress",
    tags=["Weekly Progress"],
)


# GET ALL
@router.get("/", response_model=list[WeeklyProgressResponse])
def get_all_weekly_progress(db: Session = Depends(get_db)):
    return db.query(WeeklyProgress).all()


# GET BY ID
@router.get("/{progress_id}", response_model=WeeklyProgressResponse)
def get_weekly_progress_by_id(
    progress_id: int,
    db: Session = Depends(get_db),
):
    progress = (
        db.query(WeeklyProgress)
        .filter(WeeklyProgress.id == progress_id)
        .first()
    )

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Weekly Progress not found"
        )

    return progress


# POST
@router.post("/", response_model=WeeklyProgressResponse)
def create_weekly_progress(
    progress: WeeklyProgressCreate,
    db: Session = Depends(get_db),
):
    # Check whether project exists
    project = db.query(Project).filter(
        Project.id == progress.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    new_progress = WeeklyProgress(
        **progress.model_dump()
    )

    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)

    return new_progress


# DELETE
@router.delete("/{progress_id}")
def delete_weekly_progress(
    progress_id: int,
    db: Session = Depends(get_db),
):
    progress = (
        db.query(WeeklyProgress)
        .filter(WeeklyProgress.id == progress_id)
        .first()
    )

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Weekly Progress not found"
        )

    db.delete(progress)
    db.commit()

    return {
        "message": "Weekly Progress deleted successfully"
    }