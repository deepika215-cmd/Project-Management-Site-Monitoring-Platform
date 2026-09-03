from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.site_activity_log import SiteActivityLog
from app.models.project import Project
from app.models.user import User

from app.core.permissions import role_required

from app.schemas.site_activity_log_schema import (
    SiteActivityLogCreate,
    SiteActivityLogResponse,
)


router = APIRouter(
    prefix="/site-activity-logs",
    tags=["Site Activity Logs"],
)


# =========================================================
# CREATE SITE ACTIVITY LOG
# ADMIN / MANAGER / ENGINEER
# =========================================================
@router.post(
    "/",
    response_model=SiteActivityLogResponse
)
def create_site_activity_log(
    activity: SiteActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    ),
):

    project = db.query(Project).filter(
        Project.id == activity.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot add activity log to a closed project"
        )

    new_activity = SiteActivityLog(
        **activity.model_dump()
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity


# =========================================================
# GET ALL SITE ACTIVITY LOGS
# ADMIN / MANAGER / ENGINEER / CLIENT
# =========================================================
@router.get(
    "/",
    response_model=list[SiteActivityLogResponse]
)
def get_all_site_activity_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(
            ["ADMIN", "MANAGER", "ENGINEER", "CLIENT"]
        )
    ),
):

    return (
        db.query(SiteActivityLog)
        .order_by(
            SiteActivityLog.activity_date.desc(),
            SiteActivityLog.activity_time.desc()
        )
        .all()
    )


# =========================================================
# GET SITE ACTIVITY LOG BY ID
# ADMIN / MANAGER / ENGINEER / CLIENT
# =========================================================
@router.get(
    "/{log_id}",
    response_model=SiteActivityLogResponse
)
def get_site_activity_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(
            ["ADMIN", "MANAGER", "ENGINEER", "CLIENT"]
        )
    ),
):

    activity = db.query(SiteActivityLog).filter(
        SiteActivityLog.id == log_id
    ).first()

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Site Activity Log not found"
        )

    return activity


# =========================================================
# UPDATE SITE ACTIVITY LOG
# ADMIN / MANAGER / ENGINEER
# =========================================================
@router.put(
    "/{log_id}",
    response_model=SiteActivityLogResponse
)
def update_site_activity_log(
    log_id: int,
    updated_activity: SiteActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(
            ["ADMIN", "MANAGER", "ENGINEER"]
        )
    ),
):

    activity = db.query(SiteActivityLog).filter(
        SiteActivityLog.id == log_id
    ).first()

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Site Activity Log not found"
        )

    project = db.query(Project).filter(
        Project.id == updated_activity.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot update activity log for a closed project"
        )

    for key, value in updated_activity.model_dump().items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)

    return activity


# =========================================================
# DELETE SITE ACTIVITY LOG
# ADMIN / MANAGER
# =========================================================
@router.delete(
    "/{log_id}"
)
def delete_site_activity_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    ),
):

    activity = db.query(SiteActivityLog).filter(
        SiteActivityLog.id == log_id
    ).first()

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Site Activity Log not found"
        )

    db.delete(activity)
    db.commit()

    return {
        "message": "Site Activity Log deleted successfully"
    }