from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.procurement import Procurement
from app.schemas.procurement_schema import (
    ProcurementCreate,
    ProcurementResponse,
    ProcurementReportResponse,
)


router = APIRouter(
    prefix="/procurement",
    tags=["Procurement"],
)


# Create Procurement
@router.post(
    "/",
    response_model=ProcurementResponse
)
def create_procurement(
    procurement: ProcurementCreate,
    db: Session = Depends(get_db),
):
    new_procurement = Procurement(
        **procurement.model_dump()
    )

    db.add(new_procurement)
    db.commit()
    db.refresh(new_procurement)

    return new_procurement


# Get All Procurements
@router.get(
    "/",
    response_model=list[ProcurementResponse]
)
def get_procurements(
    db: Session = Depends(get_db),
):
    return db.query(Procurement).all()


# Procurement Report
# This route must be before /{procurement_id}
@router.get(
    "/report",
    response_model=ProcurementReportResponse
)
def get_procurement_report(
    db: Session = Depends(get_db),
):
    procurements = db.query(Procurement).all()

    total_requests = len(procurements)

    pending_count = 0
    approved_count = 0
    rejected_count = 0
    completed_count = 0

    total_quantity = 0
    used_quantity = 0

    for procurement in procurements:

        status = (
            procurement.status or ""
        ).strip().upper()

        if status == "PENDING":
            pending_count += 1

        elif status == "APPROVED":
            approved_count += 1

        elif status == "REJECTED":
            rejected_count += 1

        elif status in [
            "COMPLETED",
            "RECEIVED",
            "DELIVERED"
        ]:
            completed_count += 1

        quantity = procurement.quantity or 0
        used = procurement.used or 0

        total_quantity += quantity
        used_quantity += used

    remaining_quantity = (
        total_quantity - used_quantity
    )

    return ProcurementReportResponse(
        total_requests=total_requests,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        completed_count=completed_count,
        total_quantity=total_quantity,
        used_quantity=used_quantity,
        remaining_quantity=remaining_quantity,
    )


# Get Procurement By ID
@router.get(
    "/{procurement_id}",
    response_model=ProcurementResponse
)
def get_procurement(
    procurement_id: int,
    db: Session = Depends(get_db),
):
    procurement = (
        db.query(Procurement)
        .filter(
            Procurement.id == procurement_id
        )
        .first()
    )

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found",
        )

    return procurement


# Update Procurement
@router.put(
    "/{procurement_id}",
    response_model=ProcurementResponse
)
def update_procurement(
    procurement_id: int,
    procurement_data: ProcurementCreate,
    db: Session = Depends(get_db),
):
    procurement = (
        db.query(Procurement)
        .filter(
            Procurement.id == procurement_id
        )
        .first()
    )

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found",
        )

    for key, value in procurement_data.model_dump().items():
        setattr(
            procurement,
            key,
            value
        )

    db.commit()
    db.refresh(procurement)

    return procurement


# Delete Procurement
@router.delete(
    "/{procurement_id}"
)
def delete_procurement(
    procurement_id: int,
    db: Session = Depends(get_db),
):
    procurement = (
        db.query(Procurement)
        .filter(
            Procurement.id == procurement_id
        )
        .first()
    )

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found",
        )

    db.delete(procurement)
    db.commit()

    return {
        "message": "Procurement deleted successfully"
    }
