from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.delay_record import DelayRecord
from app.schemas.delay_record_schema import (
    DelayRecordCreate,
    DelayRecordResponse
)


router = APIRouter(
    prefix="/delay-records",
    tags=["Delay Tracking"]
)


@router.post("/", response_model=DelayRecordResponse)
def create_delay(
    delay: DelayRecordCreate,
    db: Session = Depends(get_db)
):
    new_delay = DelayRecord(**delay.model_dump())

    db.add(new_delay)
    db.commit()
    db.refresh(new_delay)

    return new_delay


@router.get("/", response_model=list[DelayRecordResponse])
def get_delays(db: Session = Depends(get_db)):
    return db.query(DelayRecord).all()


@router.get("/{delay_id}", response_model=DelayRecordResponse)
def get_delay(
    delay_id: int,
    db: Session = Depends(get_db)
):
    delay = db.query(DelayRecord).filter(
        DelayRecord.id == delay_id
    ).first()

    if not delay:
        raise HTTPException(
            status_code=404,
            detail="Delay Record not found"
        )

    return delay

@router.put("/{delay_id}", response_model=DelayRecordResponse)
def update_delay(
    delay_id: int,
    delay: DelayRecordCreate,
    db: Session = Depends(get_db)
):
    existing_delay = db.query(DelayRecord).filter(
        DelayRecord.id == delay_id
    ).first()

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


@router.delete("/{delay_id}")
def delete_delay(
    delay_id: int,
    db: Session = Depends(get_db)
):
    existing_delay = db.query(DelayRecord).filter(
        DelayRecord.id == delay_id
    ).first()

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