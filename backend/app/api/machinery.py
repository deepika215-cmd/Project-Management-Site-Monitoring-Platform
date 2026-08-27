from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.machinery import Machinery
from app.schemas.machinery_schema import (
    MachineryCreate,
    MachineryResponse,
    MachineryStatusUpdate,
    MachineryHoursUpdate
)


router = APIRouter(
    prefix="/machinery",
    tags=["Machinery"]
)


# =========================================================
# Create Machinery
# =========================================================

@router.post("/", response_model=MachineryResponse)
def create_machinery(
    machinery: MachineryCreate,
    db: Session = Depends(get_db)
):
    new_machinery = Machinery(
        name=machinery.name,
        machinery_type=machinery.machinery_type,
        location=machinery.location,
        status=machinery.status,
        operator=machinery.operator,
        hours_used=machinery.hours_used,
        project_id=machinery.project_id
    )

    db.add(new_machinery)
    db.commit()
    db.refresh(new_machinery)

    return new_machinery


# =========================================================
# Get All Machinery
# =========================================================

@router.get("/", response_model=list[MachineryResponse])
def get_machinery(
    db: Session = Depends(get_db)
):
    return db.query(Machinery).all()


# =========================================================
# Get Machinery By ID
# =========================================================

@router.get("/{machinery_id}", response_model=MachineryResponse)
def get_machinery_by_id(
    machinery_id: int,
    db: Session = Depends(get_db)
):
    machinery = db.query(Machinery).filter(
        Machinery.id == machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    return machinery


# =========================================================
# Update Machinery
# =========================================================

@router.put("/{machinery_id}", response_model=MachineryResponse)
def update_machinery(
    machinery_id: int,
    machinery_data: MachineryCreate,
    db: Session = Depends(get_db)
):
    machinery = db.query(Machinery).filter(
        Machinery.id == machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    machinery.name = machinery_data.name
    machinery.machinery_type = machinery_data.machinery_type
    machinery.location = machinery_data.location
    machinery.status = machinery_data.status
    machinery.operator = machinery_data.operator
    machinery.hours_used = machinery_data.hours_used
    machinery.project_id = machinery_data.project_id

    db.commit()
    db.refresh(machinery)

    return machinery


# =========================================================
# Update Machinery Status
# =========================================================

@router.put(
    "/{machinery_id}/status",
    response_model=MachineryResponse
)
def update_machinery_status(
    machinery_id: int,
    status_data: MachineryStatusUpdate,
    db: Session = Depends(get_db)
):
    machinery = db.query(Machinery).filter(
        Machinery.id == machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    machinery.status = status_data.status

    db.commit()
    db.refresh(machinery)

    return machinery


# =========================================================
# Add Machinery Usage Hours
# =========================================================

@router.put(
    "/{machinery_id}/hours",
    response_model=MachineryResponse
)
def update_machinery_hours(
    machinery_id: int,
    hours_data: MachineryHoursUpdate,
    db: Session = Depends(get_db)
):
    machinery = db.query(Machinery).filter(
        Machinery.id == machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    machinery.hours_used += hours_data.hours

    db.commit()
    db.refresh(machinery)

    return machinery


# =========================================================
# Delete Machinery
# =========================================================

@router.delete("/{machinery_id}")
def delete_machinery(
    machinery_id: int,
    db: Session = Depends(get_db)
):
    machinery = db.query(Machinery).filter(
        Machinery.id == machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    db.delete(machinery)
    db.commit()

    return {
        "message": "Machinery deleted successfully"
    }
