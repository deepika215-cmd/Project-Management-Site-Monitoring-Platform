from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.delay_record import DelayRecord
from app.models.notification import Notification

from app.schemas.delay_record_schema import (
    DelayRecordCreate,
    DelayRecordResponse
)


router = APIRouter(
    prefix="/delay-records",
    tags=["Delay Tracking"]
)


# ============================================================
# CREATE DELAY RECORD
#
# Automatically creates notifications for:
# - MANAGER
# - ADMIN
# ============================================================

@router.post("/", response_model=DelayRecordResponse)
def create_delay(
    delay: DelayRecordCreate,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Create Delay Record
    # --------------------------------------------------------

    new_delay = DelayRecord(
        project_id=delay.project_id,
        delay_date=delay.delay_date,
        reason=delay.reason,
        duration_hours=delay.duration_hours,
        affected_work=delay.affected_work,
        impact=delay.impact
    )

    db.add(new_delay)
    db.commit()
    db.refresh(new_delay)

    # --------------------------------------------------------
    # Notification Message
    # --------------------------------------------------------

    notification_message = (
        f"Delay reported for Project {delay.project_id}: "
        f"{delay.reason}. "
        f"Affected work: {delay.affected_work}. "
        f"Duration: {delay.duration_hours} hours. "
        f"Impact: {delay.impact}"
    )

    # --------------------------------------------------------
    # Create Manager Notification
    # --------------------------------------------------------

    manager_notification = Notification(
        title="Project Delay Reported",
        message=notification_message,
        recipient="MANAGER",
        status="Unread"
    )

    # --------------------------------------------------------
    # Create Admin Notification
    # --------------------------------------------------------

    admin_notification = Notification(
        title="Project Delay Reported",
        message=notification_message,
        recipient="ADMIN",
        status="Unread"
    )

    db.add(manager_notification)
    db.add(admin_notification)

    # Save notifications
    db.commit()

    return new_delay


# ============================================================
# GET ALL DELAY RECORDS
# ============================================================

@router.get("/", response_model=list[DelayRecordResponse])
def get_delays(
    db: Session = Depends(get_db)
):
    return db.query(DelayRecord).all()


# ============================================================
# GET DELAY BY ID
# ============================================================

@router.get("/{delay_id}", response_model=DelayRecordResponse)
def get_delay(
    delay_id: int,
    db: Session = Depends(get_db)
):
    delay = (
        db.query(DelayRecord)
        .filter(DelayRecord.id == delay_id)
        .first()
    )

    if not delay:
        raise HTTPException(
            status_code=404,
            detail="Delay Record not found"
        )

    return delay


# ============================================================
# UPDATE DELAY RECORD
# ============================================================

@router.put("/{delay_id}", response_model=DelayRecordResponse)
def update_delay(
    delay_id: int,
    delay: DelayRecordCreate,
    db: Session = Depends(get_db)
):
    existing_delay = (
        db.query(DelayRecord)
        .filter(DelayRecord.id == delay_id)
        .first()
    )

    if not existing_delay:
        raise HTTPException(
            status_code=404,
            detail="Delay Record not found"
        )

    existing_delay.project_id = delay.project_id
    existing_delay.delay_date = delay.delay_date
    existing_delay.reason = delay.reason
    existing_delay.duration_hours = delay.duration_hours
    existing_delay.affected_work = delay.affected_work
    existing_delay.impact = delay.impact

    db.commit()
    db.refresh(existing_delay)

    return existing_delay


# ============================================================
# DELETE DELAY RECORD
# ============================================================

@router.delete("/{delay_id}")
def delete_delay(
    delay_id: int,
    db: Session = Depends(get_db)
):
    existing_delay = (
        db.query(DelayRecord)
        .filter(DelayRecord.id == delay_id)
        .first()
    )

    if not existing_delay:
        raise HTTPException(
            status_code=404,
            detail="Delay Record not found"
        )

    db.delete(existing_delay)
    db.commit()

    return {
        "message": "Delay Record deleted successfully"
    }