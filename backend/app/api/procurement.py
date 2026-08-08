from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.procurement import Procurement
from app.schemas.procurement_schema import (
    ProcurementCreate,
    ProcurementResponse,
    ProcurementUsage,
    ProcurementUtilization
)


router = APIRouter(
    prefix="/procurement",
    tags=["Procurement"]
)


# --------------------------------------------------
# Create Procurement
# --------------------------------------------------

@router.post("/", response_model=ProcurementResponse)
def create_procurement(
    procurement: ProcurementCreate,
    db: Session = Depends(get_db)
):
    if procurement.quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity cannot be negative"
        )

    new_procurement = Procurement(
        **procurement.model_dump(),
        used=0
    )

    db.add(new_procurement)
    db.commit()
    db.refresh(new_procurement)

    return new_procurement


# --------------------------------------------------
# Get All Procurements
# --------------------------------------------------

@router.get("/", response_model=list[ProcurementResponse])
def get_procurements(
    db: Session = Depends(get_db)
):
    return db.query(Procurement).all()


# --------------------------------------------------
# Get Procurement By ID
# --------------------------------------------------

@router.get("/{procurement_id}", response_model=ProcurementResponse)
def get_procurement(
    procurement_id: int,
    db: Session = Depends(get_db)
):
    procurement = db.query(Procurement).filter(
        Procurement.id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    return procurement


# --------------------------------------------------
# Update Procurement
# --------------------------------------------------

@router.put("/{procurement_id}", response_model=ProcurementResponse)
def update_procurement(
    procurement_id: int,
    data: ProcurementCreate,
    db: Session = Depends(get_db)
):
    procurement = db.query(Procurement).filter(
        Procurement.id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    if data.quantity < procurement.used:
        raise HTTPException(
            status_code=400,
            detail="Quantity cannot be less than already used quantity"
        )

    for key, value in data.model_dump().items():
        setattr(procurement, key, value)

    # Automatically update status
    if procurement.used >= procurement.quantity:
        procurement.status = "Fully Used"
    else:
        procurement.status = "Available"

    db.commit()
    db.refresh(procurement)

    return procurement


# --------------------------------------------------
# Delete Procurement
# --------------------------------------------------

@router.delete("/{procurement_id}")
def delete_procurement(
    procurement_id: int,
    db: Session = Depends(get_db)
):
    procurement = db.query(Procurement).filter(
        Procurement.id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    db.delete(procurement)
    db.commit()

    return {
        "message": "Procurement deleted successfully"
    }


# --------------------------------------------------
# Use Procurement
# --------------------------------------------------

@router.put(
    "/{procurement_id}/use",
    response_model=ProcurementResponse
)
def use_procurement(
    procurement_id: int,
    usage: ProcurementUsage,
    db: Session = Depends(get_db)
):
    procurement = db.query(Procurement).filter(
        Procurement.id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    if usage.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Usage quantity must be greater than zero"
        )

    available_quantity = (
        procurement.quantity - procurement.used
    )

    if usage.quantity > available_quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough procurement available"
        )

    procurement.used += usage.quantity

    if procurement.used >= procurement.quantity:
        procurement.status = "Fully Used"
    else:
        procurement.status = "Available"

    db.commit()
    db.refresh(procurement)

    return procurement


# --------------------------------------------------
# Release Procurement
# --------------------------------------------------

@router.put(
    "/{procurement_id}/release",
    response_model=ProcurementResponse
)
def release_procurement(
    procurement_id: int,
    usage: ProcurementUsage,
    db: Session = Depends(get_db)
):
    procurement = db.query(Procurement).filter(
        Procurement.id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    if usage.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Release quantity must be greater than zero"
        )

    if usage.quantity > procurement.used:
        raise HTTPException(
            status_code=400,
            detail="Cannot release more procurement than currently used"
        )

    procurement.used -= usage.quantity

    if procurement.used < procurement.quantity:
        procurement.status = "Available"

    db.commit()
    db.refresh(procurement)

    return procurement


# --------------------------------------------------
# Get Procurement Utilization
# --------------------------------------------------

@router.get(
    "/{procurement_id}/utilization",
    response_model=ProcurementUtilization
)
def get_procurement_utilization(
    procurement_id: int,
    db: Session = Depends(get_db)
):
    procurement = db.query(Procurement).filter(
        Procurement.id == procurement_id
    ).first()

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found"
        )

    available_quantity = (
        procurement.quantity - procurement.used
    )

    if procurement.quantity > 0:
        utilization_percentage = (
            procurement.used / procurement.quantity
        ) * 100
    else:
        utilization_percentage = 0

    return {
        "procurement_id": procurement.id,
        "item_name": procurement.item_name,
        "total_quantity": procurement.quantity,
        "used_quantity": procurement.used,
        "available_quantity": available_quantity,
        "utilization_percentage": round(
            utilization_percentage,
            2
        ),
        "status": procurement.status
    }