from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.worker import Worker
from app.models.contractor import Contractor
from app.models.user import User

from app.schemas.worker_schema import (
    WorkerCreate,
    WorkerResponse
)


router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


# ============================================================
# CREATE WORKER
# ============================================================

@router.post(
    "/",
    response_model=WorkerResponse
)
def create_worker(
    worker: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    # Validate contractor if supplied
    if worker.contractor_id is not None:

        contractor = db.query(
            Contractor
        ).filter(
            Contractor.id == worker.contractor_id
        ).first()

        if not contractor:
            raise HTTPException(
                status_code=404,
                detail="Contractor not found"
            )

    new_worker = Worker(
        **worker.model_dump()
    )

    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return new_worker


# ============================================================
# GET ALL WORKERS
# ============================================================

@router.get(
    "/",
    response_model=list[WorkerResponse]
)
def get_workers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):

    return db.query(
        Worker
    ).order_by(
        Worker.id.desc()
    ).all()


# ============================================================
# GET WORKER BY ID
# ============================================================

@router.get(
    "/{worker_id}",
    response_model=WorkerResponse
)
def get_worker(
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

    return worker


# ============================================================
# UPDATE WORKER
# ============================================================

@router.put(
    "/{worker_id}",
    response_model=WorkerResponse
)
def update_worker(
    worker_id: int,
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
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

    # Validate contractor
    if worker_data.contractor_id is not None:

        contractor = db.query(
            Contractor
        ).filter(
            Contractor.id == worker_data.contractor_id
        ).first()

        if not contractor:
            raise HTTPException(
                status_code=404,
                detail="Contractor not found"
            )

    for key, value in worker_data.model_dump().items():
        setattr(worker, key, value)

    db.commit()
    db.refresh(worker)

    return worker


# ============================================================
# DELETE WORKER
# ============================================================

@router.delete(
    "/{worker_id}"
)
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN"])
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

    db.delete(worker)
    db.commit()

    return {
        "message": "Worker deleted successfully"
    }
