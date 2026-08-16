from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.site_activity_log import SiteActivityLog
from app.schemas.site_activity_log_schema import (
    SiteActivityLogCreate,
    SiteActivityLogResponse
)


router = APIRouter(
    prefix="/site-activity-logs",
    tags=["Site Activity Logs"]
)


@router.post("/", response_model=SiteActivityLogResponse)
def create_activity_log(
    activity: SiteActivityLogCreate,
    db: Session = Depends(get_db)
):
    new_activity = SiteActivityLog(**activity.model_dump())

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity


@router.get("/", response_model=list[SiteActivityLogResponse])
def get_activity_logs(
    db: Session = Depends(get_db)
):
    return db.query(SiteActivityLog).all()


@router.get("/{activity_id}", response_model=SiteActivityLogResponse)
def get_activity_log(
    activity_id: int,
    db: Session = Depends(get_db)
):
    activity = db.query(SiteActivityLog).filter(
        SiteActivityLog.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Site Activity Log not found"
        )

    return activity


@router.put("/{activity_id}", response_model=SiteActivityLogResponse)
def update_activity_log(
    activity_id: int,
    activity_data: SiteActivityLogCreate,
    db: Session = Depends(get_db)
):
    activity = db.query(SiteActivityLog).filter(
        SiteActivityLog.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Site Activity Log not found"
        )

    for key, value in activity_data.model_dump().items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)

    return activity


@router.delete("/{activity_id}")
def delete_activity_log(
    activity_id: int,
    db: Session = Depends(get_db)
):
    activity = db.query(SiteActivityLog).filter(
        SiteActivityLog.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Site Activity Log not found"
        )

    db.delete(activity)
    db.commit()

    return {
        "message": "Site Activity Log deleted successfully"
    }
