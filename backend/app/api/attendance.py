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

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


# ============================================================
# MODULE 8 - GET RESPONSIBLE PROJECT MANAGER
# ============================================================

def get_project_manager_email(
    db: Session,
    project_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return None

    if not project.manager_id:
        return None

    manager = (
        db.query(User)
        .filter(
            User.id == project.manager_id,
            User.role == "MANAGER",
        )
        .first()
    )

    if not manager:
        return None

    return manager.email


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

    # --------------------------------------------------------
    # MODULE 8 - ATTENDANCE ALERT
    #
    # Generate notifications for:
    # ABSENT
    # LATE
    # HALF_DAY
    #
    # Notification goes only to the responsible
    # Project Manager.
    # --------------------------------------------------------

    attendance_status = (
        new_attendance.status or ""
    ).strip().upper()

    if (
        attendance_status in [
            "ABSENT",
            "LATE",
            "HALF_DAY",
            "HALF-DAY",
            "HALFDAY",
        ]
        and new_attendance.project_id is not None
    ):

        worker_name = (
            getattr(worker, "name", None)
            or f"Worker #{worker.id}"
        )

        title_map = {
            "ABSENT": "Attendance Alert",
            "LATE": "Late Attendance Alert",
            "HALF_DAY": "Half-Day Attendance Alert",
            "HALF-DAY": "Half-Day Attendance Alert",
            "HALFDAY": "Half-Day Attendance Alert",
        }

        title = title_map.get(
            attendance_status,
            "Attendance Alert"
        )

        message = (
            f"{worker_name} was marked "
            f"{new_attendance.status} "
            f"on {new_attendance.date}."
        )

        message += (
            f" Project: #{new_attendance.project_id}."
        )

        # ----------------------------------------------------
        # Find responsible Project Manager
        # ----------------------------------------------------

        manager_email = get_project_manager_email(
            db=db,
            project_id=new_attendance.project_id,
        )

        if manager_email:

            create_notification(
                db=db,
                title=title,
                message=message,
                recipient=manager_email,
            )

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

    attendance_records = db.query(
        Attendance
    ).all()

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

    total_records = len(attendance_records)

    present_count = 0
    absent_count = 0
    late_count = 0
    half_day_count = 0

    total_working_hours = 0.0

    for record in attendance_records:

        status = (
            record.status or ""
        ).strip().upper()

        if status == "PRESENT":
            present_count += 1

        elif status == "ABSENT":
            absent_count += 1

        elif status == "LATE":
            late_count += 1

        elif status in [
            "HALF_DAY",
            "HALF-DAY",
            "HALFDAY"
        ]:
            half_day_count += 1

        total_working_hours += (
            record.working_hours or 0.0
        )

    attended_records = (
        present_count
        + late_count
        + half_day_count
    )

    attendance_percentage = (
        attended_records / total_records
    ) * 100

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
    # Save old attendance status
    # --------------------------------------------------------

    old_status = attendance.status

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    for key, value in attendance_data.model_dump().items():
        setattr(
            attendance,
            key,
            value
        )

    db.commit()
    db.refresh(attendance)

    # --------------------------------------------------------
    # MODULE 8 - ATTENDANCE ALERT ON UPDATE
    #
    # If attendance is changed to ABSENT, LATE or HALF_DAY,
    # notify the responsible Project Manager.
    # --------------------------------------------------------

    new_status = (
        attendance.status or ""
    ).strip().upper()

    if (
        old_status != attendance.status
        and new_status in [
            "ABSENT",
            "LATE",
            "HALF_DAY",
            "HALF-DAY",
            "HALFDAY",
        ]
        and attendance.project_id is not None
    ):

        worker_name = (
            getattr(worker, "name", None)
            or f"Worker #{worker.id}"
        )

        title_map = {
            "ABSENT": "Attendance Alert",
            "LATE": "Late Attendance Alert",
            "HALF_DAY": "Half-Day Attendance Alert",
            "HALF-DAY": "Half-Day Attendance Alert",
            "HALFDAY": "Half-Day Attendance Alert",
        }

        title = title_map.get(
            new_status,
            "Attendance Alert"
        )

        message = (
            f"{worker_name}'s attendance was updated to "
            f"{attendance.status} on {attendance.date}."
        )

        message += (
            f" Project: #{attendance.project_id}."
        )

        # ----------------------------------------------------
        # Find responsible Project Manager
        # ----------------------------------------------------

        manager_email = get_project_manager_email(
            db=db,
            project_id=attendance.project_id,
        )

        if manager_email:

            create_notification(
                db=db,
                title=title,
                message=message,
                recipient=manager_email,
            )

    return attendance


# ============================================================
# DELETE ATTENDANCE
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.delete(
    "/{attendance_id}"
)
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