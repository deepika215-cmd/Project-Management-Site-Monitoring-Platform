from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.attendance import Attendance
from app.schemas.attendance_schema import AttendanceCreate, AttendanceResponse

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


@router.post("/", response_model=AttendanceResponse)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    new_attendance = Attendance(**attendance.model_dump())

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance


@router.get("/")
def get_attendance(db: Session = Depends(get_db)):
    return db.query(Attendance).all()


@router.get("/{attendance_id}")
def get_attendance_by_id(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    return attendance


@router.put("/{attendance_id}")
def update_attendance(
    attendance_id: int,
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
):
    old = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not old:
        raise HTTPException(status_code=404, detail="Attendance not found")

    for key, value in attendance.model_dump().items():
        setattr(old, key, value)

    db.commit()
    db.refresh(old)

    return old


@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    db.delete(attendance)
    db.commit()

    return {"message": "Attendance deleted successfully"}