from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.attendance import Attendance
from app.models.worker import Worker

from app.schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUsage,
    AttendanceUtilization
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


# =========================================================
# Create Attendance
# =========================================================

@router.post(
    "/",
    response_model=AttendanceResponse
)
def create_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):

    # Check whether worker exists
    worker = db.query(Worker).filter(
        Worker.id == attendance.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    new_attendance = Attendance(
        **attendance.model_dump(),
        used=0
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance


# =========================================================
# Get All Attendance
# =========================================================

@router.get(
    "/",
    response_model=list[AttendanceResponse]
)
def get_attendance(
    db: Session = Depends(get_db)
):

    return db.query(Attendance).all()


# =========================================================
# Get Attendance By ID
# =========================================================

@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def get_attendance_by_id(
    attendance_id: int,
    db: Session = Depends(get_db)
):

    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    return attendance


# =========================================================
# Update Attendance
# =========================================================

@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db)
):

    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    # Check whether worker exists
    worker = db.query(Worker).filter(
        Worker.id == attendance_data.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    for key, value in attendance_data.model_dump().items():
        setattr(attendance, key, value)

    db.commit()
    db.refresh(attendance)

    return attendance


# =========================================================
# Delete Attendance
# =========================================================

@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):

    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    db.delete(attendance)
    db.commit()

    return {
        "message": "Attendance deleted successfully"
    }


# =========================================================
# Use Attendance
# =========================================================

@router.put(
    "/{attendance_id}/use",
    response_model=AttendanceResponse
)
def use_attendance(
    attendance_id: int,
    usage: AttendanceUsage,
    db: Session = Depends(get_db)
):

    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    if usage.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    # One attendance record represents one attendance unit
    available_quantity = 1 - attendance.used

    if usage.quantity > available_quantity:
        raise HTTPException(
            status_code=400,
            detail="Attendance is already fully used"
        )

    attendance.used += usage.quantity

    db.commit()
    db.refresh(attendance)

    return attendance


# =========================================================
# Release Attendance
# =========================================================

@router.put(
    "/{attendance_id}/release",
    response_model=AttendanceResponse
)
def release_attendance(
    attendance_id: int,
    usage: AttendanceUsage,
    db: Session = Depends(get_db)
):

    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    if usage.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if usage.quantity > attendance.used:
        raise HTTPException(
            status_code=400,
            detail="Cannot release more attendance than currently used"
        )

    attendance.used -= usage.quantity

    db.commit()
    db.refresh(attendance)

    return attendance


# =========================================================
# Get Attendance Utilization
# =========================================================

@router.get(
    "/{attendance_id}/utilization",
    response_model=AttendanceUtilization
)
def get_attendance_utilization(
    attendance_id: int,
    db: Session = Depends(get_db)
):

    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    total_quantity = 1

    available_quantity = (
        total_quantity - attendance.used
    )

    utilization_percentage = (
        attendance.used / total_quantity
    ) * 100

    return {
        "attendance_id": attendance.id,
        "worker_id": attendance.worker_id,
        "date": attendance.date,
        "status": attendance.status,
        "used_quantity": attendance.used,
        "available_quantity": available_quantity,
        "utilization_percentage": round(
            utilization_percentage,
            2
        )
    }