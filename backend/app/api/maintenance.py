from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.maintenance import Maintenance
from app.models.machinery import Machinery
from app.schemas.maintenance_schema import (
    MaintenanceCreate,
    MaintenanceResponse,
    MaintenanceStatusUpdate,
    MaintenanceCompletion
)


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


# =========================================================
# Create Maintenance
# =========================================================

@router.post("/", response_model=MaintenanceResponse)
def create_maintenance(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    machinery = db.query(Machinery).filter(
        Machinery.id == maintenance.machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    new_maintenance = Maintenance(
        machinery_id=maintenance.machinery_id,
        maintenance_type=maintenance.maintenance_type,
        description=maintenance.description,
        scheduled_date=maintenance.scheduled_date,
        completion_date=maintenance.completion_date,
        status=maintenance.status,
        cost=maintenance.cost,
        technician=maintenance.technician
    )

    db.add(new_maintenance)
    db.commit()
    db.refresh(new_maintenance)

    return new_maintenance


# =========================================================
# Get All Maintenance Records
# =========================================================

@router.get("/", response_model=list[MaintenanceResponse])
def get_maintenance(
    db: Session = Depends(get_db)
):
    return db.query(Maintenance).all()


# =========================================================
# Upcoming Maintenance
# IMPORTANT: This route must come BEFORE /{maintenance_id}
# =========================================================

@router.get(
    "/upcoming",
    response_model=list[MaintenanceResponse]
)
def get_upcoming_maintenance(
    db: Session = Depends(get_db)
):
    return db.query(Maintenance).filter(
        Maintenance.scheduled_date >= date.today(),
        Maintenance.status != "Completed"
    ).order_by(
        Maintenance.scheduled_date
    ).all()


# =========================================================
# Get Maintenance By ID
# =========================================================

@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def get_maintenance_by_id(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    return maintenance


# =========================================================
# Update Maintenance
# =========================================================

@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def update_maintenance(
    maintenance_id: int,
    maintenance_data: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    machinery = db.query(Machinery).filter(
        Machinery.id == maintenance_data.machinery_id
    ).first()

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    maintenance.machinery_id = maintenance_data.machinery_id
    maintenance.maintenance_type = maintenance_data.maintenance_type
    maintenance.description = maintenance_data.description
    maintenance.scheduled_date = maintenance_data.scheduled_date
    maintenance.completion_date = maintenance_data.completion_date
    maintenance.status = maintenance_data.status
    maintenance.cost = maintenance_data.cost
    maintenance.technician = maintenance_data.technician

    db.commit()
    db.refresh(maintenance)

    return maintenance


# =========================================================
# Update Maintenance Status
# =========================================================

@router.put(
    "/{maintenance_id}/status",
    response_model=MaintenanceResponse
)
def update_maintenance_status(
    maintenance_id: int,
    status_data: MaintenanceStatusUpdate,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    maintenance.status = status_data.status

    db.commit()
    db.refresh(maintenance)

    return maintenance


# =========================================================
# Complete Maintenance
# =========================================================

@router.put(
    "/{maintenance_id}/complete",
    response_model=MaintenanceResponse
)
def complete_maintenance(
    maintenance_id: int,
    completion_data: MaintenanceCompletion,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    maintenance.completion_date = completion_data.completion_date
    maintenance.status = "Completed"

    db.commit()
    db.refresh(maintenance)

    return maintenance


# =========================================================
# Delete Maintenance
# =========================================================

@router.delete("/{maintenance_id}")
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    db.delete(maintenance)
    db.commit()

    return {
        "message": "Maintenance record deleted successfully"
    }
