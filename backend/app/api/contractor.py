from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contractor import Contractor
from app.schemas.contractor_schema import (
    ContractorCreate,
    ContractorResponse,
)


router = APIRouter(
    prefix="/contractors",
    tags=["Contractors"],
)


# ============================================================
# CREATE CONTRACTOR
# ============================================================

@router.post(
    "/",
    response_model=ContractorResponse
)
def create_contractor(
    contractor: ContractorCreate,
    db: Session = Depends(get_db),
):
    new_contractor = Contractor(
        **contractor.model_dump()
    )

    db.add(new_contractor)
    db.commit()
    db.refresh(new_contractor)

    return new_contractor


# ============================================================
# GET ALL CONTRACTORS
# ============================================================

@router.get(
    "/",
    response_model=list[ContractorResponse]
)
def get_contractors(
    db: Session = Depends(get_db),
):
    return (
        db.query(Contractor)
        .order_by(Contractor.id)
        .all()
    )


# ============================================================
# GET CONTRACTOR BY ID
# ============================================================

@router.get(
    "/{contractor_id}",
    response_model=ContractorResponse
)
def get_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
):
    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    return contractor


# ============================================================
# UPDATE CONTRACTOR
# ============================================================

@router.put(
    "/{contractor_id}",
    response_model=ContractorResponse
)
def update_contractor(
    contractor_id: int,
    contractor_data: ContractorCreate,
    db: Session = Depends(get_db),
):
    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    for key, value in contractor_data.model_dump().items():
        setattr(contractor, key, value)

    db.commit()
    db.refresh(contractor)

    return contractor


# ============================================================
# DELETE CONTRACTOR
# ============================================================

@router.delete("/{contractor_id}")
def delete_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
):
    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    db.delete(contractor)
    db.commit()

    return {
        "message": "Contractor deleted successfully"
    }