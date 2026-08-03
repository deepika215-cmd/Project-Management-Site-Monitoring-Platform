from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.worker import Worker
from app.schemas.worker_schema import (
    WorkerCreate,
    WorkerResponse
)

router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


@router.post("/", response_model=WorkerResponse)
def create_worker(
    worker: WorkerCreate,
    db: Session = Depends(get_db)
):
    new_worker = Worker(**worker.dict())

    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)

    return new_worker


@router.get("/", response_model=list[WorkerResponse])
def get_workers(
    db: Session = Depends(get_db)
):
    return db.query(Worker).all()


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    return worker


@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(
    worker_id: int,
    worker_data: WorkerCreate,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
        Worker.id == worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    for key, value in worker_data.dict().items():
        setattr(worker, key, value)

    db.commit()
    db.refresh(worker)

    return worker


@router.delete("/{worker_id}")
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.query(Worker).filter(
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