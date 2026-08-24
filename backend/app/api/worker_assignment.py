from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.worker import Worker
from app.models.contractor import Contractor
from app.models.project import Project
from app.models.worker_assignment import WorkerAssignment
from app.models.user import User

from app.schemas.worker_assignment_schema import (
    WorkerAssignmentCreate,
    WorkerAssignmentResponse
)


router = APIRouter(
    prefix="/worker-assignments",
    tags=["Worker Assignments"]
)


# ============================================================
# CREATE WORKER ASSIGNMENT
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.post(
    "/",
    response_model=WorkerAssignmentResponse
)
def create_worker_assignment(
    assignment: WorkerAssignmentCreate,
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
        Worker.id == assignment.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # --------------------------------------------------------
    # Check contractor
    # --------------------------------------------------------

    contractor = db.query(
        Contractor
    ).filter(
        Contractor.id == assignment.contractor_id
    ).first()

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found"
        )

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    project = db.query(
        Project
    ).filter(
        Project.id == assignment.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Prevent multiple active assignments
    # --------------------------------------------------------

    existing_assignment = db.query(
        WorkerAssignment
    ).filter(
        WorkerAssignment.worker_id == assignment.worker_id,
        WorkerAssignment.assignment_status == "ACTIVE"
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail=(
                "Worker already has an active assignment. "
                "Close the current assignment before "
                "assigning the worker to another project."
            )
        )

    # --------------------------------------------------------
    # Create assignment
    # --------------------------------------------------------

    new_assignment = WorkerAssignment(
        worker_id=assignment.worker_id,
        contractor_id=assignment.contractor_id,
        project_id=assignment.project_id,
        work_activity=assignment.work_activity,
        assignment_start_date=assignment.assignment_start_date,
        assignment_end_date=assignment.assignment_end_date,
        assignment_status=assignment.assignment_status
    )

    db.add(new_assignment)

    # Update worker's current contractor
    worker.contractor_id = assignment.contractor_id

    db.commit()
    db.refresh(new_assignment)

    return new_assignment


# ============================================================
# GET ALL ASSIGNMENTS
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[WorkerAssignmentResponse]
)
def get_worker_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    return db.query(
        WorkerAssignment
    ).order_by(
        WorkerAssignment.id.desc()
    ).all()


# ============================================================
# GET ASSIGNMENT BY ID
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/{assignment_id}",
    response_model=WorkerAssignmentResponse
)
def get_worker_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    assignment = db.query(
        WorkerAssignment
    ).filter(
        WorkerAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Worker assignment not found"
        )

    return assignment


# ============================================================
# CLOSE WORKER ASSIGNMENT
# Allowed roles: ADMIN, MANAGER
# ============================================================

@router.put(
    "/{assignment_id}/close",
    response_model=WorkerAssignmentResponse
)
def close_worker_assignment(
    assignment_id: int,
    assignment_end_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    assignment = db.query(
        WorkerAssignment
    ).filter(
        WorkerAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Worker assignment not found"
        )

    if assignment.assignment_status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Assignment is already closed"
        )

    assignment.assignment_status = "COMPLETED"
    assignment.assignment_end_date = assignment_end_date

    db.commit()
    db.refresh(assignment)

    return assignment


# ============================================================
# GET WORKER ASSIGNMENT HISTORY
# Allowed roles: ADMIN, MANAGER, ENGINEER
# ============================================================

@router.get(
    "/worker/{worker_id}/history",
    response_model=list[WorkerAssignmentResponse]
)
def get_worker_assignment_history(
    worker_id: int,
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
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # --------------------------------------------------------
    # Return assignment history
    # --------------------------------------------------------

    return db.query(
        WorkerAssignment
    ).filter(
        WorkerAssignment.worker_id == worker_id
    ).order_by(
        WorkerAssignment.id.desc()
    ).all()