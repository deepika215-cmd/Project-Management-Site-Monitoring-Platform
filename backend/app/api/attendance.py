from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.attendance import Attendance
from app.models.worker import Worker
from app.models.worker_assignment import WorkerAssignment
from app.models.project import Project
from app.models.user import User

from app.schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryResponse,
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


# ============================================================
# CREATE ATTENDANCE
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.post(
    "/",
    response_model=AttendanceResponse
)
def create_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    # --------------------------------------------------------
    # Check worker
    # --------------------------------------------------------

    worker = db.query(
        Worker
    ).filter(
        Worker.id == attendance.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # --------------------------------------------------------
    # Check project if provided
    # --------------------------------------------------------

    if attendance.project_id is not None:

        project = db.query(
            Project
        ).filter(
            Project.id == attendance.project_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        # ----------------------------------------------------
        # Check active worker assignment
        # ----------------------------------------------------

        assignment = db.query(
            WorkerAssignment
        ).filter(
            WorkerAssignment.worker_id == attendance.worker_id,
            WorkerAssignment.project_id == attendance.project_id,
            WorkerAssignment.assignment_status == "ACTIVE"
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Worker is not actively assigned to "
                    "this project"
                )
            )

    # --------------------------------------------------------
    # Prevent duplicate attendance
    # Same worker cannot have two records on same date
    # --------------------------------------------------------

    existing_attendance = db.query(
        Attendance
    ).filter(
        Attendance.worker_id == attendance.worker_id,
        Attendance.date == attendance.date
    ).first()

    if existing_attendance:
        raise HTTPException(
            status_code=400,
            detail=(
                "Attendance already exists for this worker "
                "on this date"
            )
        )

    # --------------------------------------------------------
    # Create attendance
    # --------------------------------------------------------

    new_attendance = Attendance(
        **attendance.model_dump()
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance


# ============================================================
# ATTENDANCE SUMMARY
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/summary",
    response_model=AttendanceSummaryResponse
)
def get_attendance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    # --------------------------------------------------------
    # Get all attendance records
    # --------------------------------------------------------

    attendance_records = db.query(
        Attendance
    ).all()

    # --------------------------------------------------------
    # If no attendance records exist
    # --------------------------------------------------------

    if not attendance_records:
        return AttendanceSummaryResponse(
            total_records=0,
            present_count=0,
            absent_count=0,
            late_count=0,
            half_day_count=0,
            total_working_hours=0.0,
            attendance_percentage=0.0
        )

    # --------------------------------------------------------
    # Initialize counters
    # --------------------------------------------------------

    total_records = len(attendance_records)

    present_count = 0
    absent_count = 0
    late_count = 0
    half_day_count = 0

    total_working_hours = 0.0

    # --------------------------------------------------------
    # Calculate summary
    # --------------------------------------------------------

    for record in attendance_records:

        status = (record.status or "").strip().upper()

        if status == "PRESENT":
            present_count += 1

        elif status == "ABSENT":
            absent_count += 1

        elif status == "LATE":
            late_count += 1

        elif status in ["HALF_DAY", "HALF-DAY", "HALFDAY"]:
            half_day_count += 1

        # Add working hours
        total_working_hours += record.working_hours or 0.0

    # --------------------------------------------------------
    # Calculate attendance percentage
    #
    # Present + Late + Half Day are treated as attended
    # records.
    # --------------------------------------------------------

    attended_records = (
        present_count
        + late_count
        + half_day_count
    )

    attendance_percentage = (
        attended_records / total_records
    ) * 100

    # --------------------------------------------------------
    # Return summary
    # --------------------------------------------------------

    return AttendanceSummaryResponse(
        total_records=total_records,
        present_count=present_count,
        absent_count=absent_count,
        late_count=late_count,
        half_day_count=half_day_count,
        total_working_hours=round(
            total_working_hours,
            2
        ),
        attendance_percentage=round(
            attendance_percentage,
            2
        )
    )


# ============================================================
# GET ALL ATTENDANCE
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[AttendanceResponse]
)
def get_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    return db.query(
        Attendance
    ).order_by(
        Attendance.id.desc()
    ).all()


# ============================================================
# GET ATTENDANCE BY ID
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def get_attendance_by_id(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    attendance = db.query(
        Attendance
    ).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    return attendance


# ============================================================
# UPDATE ATTENDANCE
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    attendance = db.query(
        Attendance
    ).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    # --------------------------------------------------------
    # Check worker
    # --------------------------------------------------------

    worker = db.query(
        Worker
    ).filter(
        Worker.id == attendance_data.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    if attendance_data.project_id is not None:

        project = db.query(
            Project
        ).filter(
            Project.id == attendance_data.project_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        # ----------------------------------------------------
        # Check active assignment
        # ----------------------------------------------------

        assignment = db.query(
            WorkerAssignment
        ).filter(
            WorkerAssignment.worker_id == attendance_data.worker_id,
            WorkerAssignment.project_id == attendance_data.project_id,
            WorkerAssignment.assignment_status == "ACTIVE"
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Worker is not actively assigned to "
                    "this project"
                )
            )

    # --------------------------------------------------------
    # Prevent duplicate date
    # --------------------------------------------------------

    duplicate = db.query(
        Attendance
    ).filter(
        Attendance.worker_id == attendance_data.worker_id,
        Attendance.date == attendance_data.date,
        Attendance.id != attendance_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail=(
                "Attendance already exists for this worker "
                "on this date"
            )
        )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    for key, value in attendance_data.model_dump().items():
        setattr(attendance, key, value)

    db.commit()
    db.refresh(attendance)

    return attendance


# ============================================================
# DELETE ATTENDANCE
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    attendance = db.query(
        Attendance
    ).filter(
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