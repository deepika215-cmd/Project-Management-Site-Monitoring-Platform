from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.daily_progress import DailyProgress
from app.schemas.daily_progress_schema import (
    DailyProgressCreate,
    DailyProgressResponse,
)

router = APIRouter(
    prefix="/daily-progress",
    tags=["Daily Progress"],
)

# GET ALL
@router.get("/", response_model=list[DailyProgressResponse])
def get_all_daily_progress(db: Session = Depends(get_db)):
    progress = db.query(DailyProgress).all()
    return progress


# GET BY ID  ← Add this here
@router.get("/{progress_id}", response_model=DailyProgressResponse)
def get_daily_progress_by_id(
    progress_id: int,
    db: Session = Depends(get_db),
):
    progress = (
        db.query(DailyProgress)
        .filter(DailyProgress.id == progress_id)
        .first()
    )

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    return progress

@router.put("/{progress_id}", response_model=DailyProgressResponse)
def update_daily_progress(
    progress_id: int,
    updated_progress: DailyProgressCreate,
    db: Session = Depends(get_db),
):
    progress = (
        db.query(DailyProgress)
        .filter(DailyProgress.id == progress_id)
        .first()
    )

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    for key, value in updated_progress.model_dump().items():
        setattr(progress, key, value)

    db.commit()
    db.refresh(progress)

    return progress

@router.delete("/{progress_id}")
def delete_daily_progress(
    progress_id: int,
    db: Session = Depends(get_db),
):
    progress = (
        db.query(DailyProgress)
        .filter(DailyProgress.id == progress_id)
        .first()
    )

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
# POST
@router.post("/", response_model=DailyProgressResponse)
def create_daily_progress(
    progress: DailyProgressCreate,
    db: Session = Depends(get_db),
):
    new_progress = DailyProgress(**progress.model_dump())

    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)

    return new_progress