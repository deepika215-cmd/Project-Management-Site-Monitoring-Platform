from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.shift import Shift
from app.models.worker import Worker
from app.models.project import Project
from app.models.user import User

from app.schemas.shift_schema import (
    ShiftCreate,
    ShiftResponse
)


router = APIRouter(
    prefix="/shifts",
    tags=["Shifts"]
)


# ============================================================
# CREATE SHIFT
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.post(
    "/",
    response_model=ShiftResponse
)
def create_shift(
    shift: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    # --------------------------------------------------------
    # Check worker
    # --------------------------------------------------------

    worker = db.query(
        Worker
    ).filter(
        Worker.id == shift.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    project = db.query(
        Project
    ).filter(
        Project.id == shift.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Prevent duplicate shift for same worker/date
    # --------------------------------------------------------

    existing_shift = db.query(
        Shift
    ).filter(
        Shift.worker_id == shift.worker_id,
        Shift.shift_date == shift.shift_date,
        Shift.status == "SCHEDULED"
    ).first()

    if existing_shift:
        raise HTTPException(
            status_code=400,
            detail="Worker already has a scheduled shift for this date"
        )

    # --------------------------------------------------------
    # Create shift
    # --------------------------------------------------------

    new_shift = Shift(
        **shift.model_dump()
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    return new_shift


# ============================================================
# GET ALL SHIFTS
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[ShiftResponse]
)
def get_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    return db.query(
        Shift
    ).order_by(
        Shift.id.desc()
    ).all()


# ============================================================
# GET SHIFT BY ID
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/{shift_id}",
    response_model=ShiftResponse
)
def get_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    shift = db.query(
        Shift
    ).filter(
        Shift.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(
            status_code=404,
            detail="Shift not found"
        )

    return shift


# ============================================================
# UPDATE SHIFT
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.put(
    "/{shift_id}",
    response_model=ShiftResponse
)
def update_shift(
    shift_id: int,
    shift_data: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    shift = db.query(
        Shift
    ).filter(
        Shift.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(
            status_code=404,
            detail="Shift not found"
        )

    worker = db.query(
        Worker
    ).filter(
        Worker.id == shift_data.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    project = db.query(
        Project
    ).filter(
        Project.id == shift_data.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    for key, value in shift_data.model_dump().items():
        setattr(shift, key, value)

    db.commit()
    db.refresh(shift)

    return shift


# ============================================================
# CANCEL SHIFT
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.put(
    "/{shift_id}/cancel",
    response_model=ShiftResponse
)
def cancel_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    shift = db.query(
        Shift
    ).filter(
        Shift.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(
            status_code=404,
            detail="Shift not found"
        )

    if shift.status == "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Completed shift cannot be cancelled"
        )

    shift.status = "CANCELLED"

    db.commit()
    db.refresh(shift)

    return shift


# ============================================================
# COMPLETE SHIFT
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.put(
    "/{shift_id}/complete",
    response_model=ShiftResponse
)
def complete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    shift = db.query(
        Shift
    ).filter(
        Shift.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(
            status_code=404,
            detail="Shift not found"
        )

    if shift.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Cancelled shift cannot be completed"
        )

    shift.status = "COMPLETED"

    db.commit()
    db.refresh(shift)

    return shift


# ============================================================
# GET WORKER SHIFTS
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/worker/{worker_id}",
    response_model=list[ShiftResponse]
)
def get_worker_shifts(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    worker = db.query(
        Worker
    ).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    return db.query(
        Shift
    ).filter(
        Shift.worker_id == worker_id
    ).order_by(
        Shift.shift_date.desc()
    ).all()