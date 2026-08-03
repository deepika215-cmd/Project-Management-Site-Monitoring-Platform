from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.procurement import Procurement
from app.schemas.procurement_schema import ProcurementCreate, ProcurementResponse

router = APIRouter(
    prefix="/procurement",
    tags=["Procurement"]
)


@router.post("/", response_model=ProcurementResponse)
def create_procurement(procurement: ProcurementCreate, db: Session = Depends(get_db)):
    new_procurement = Procurement(**procurement.model_dump())
    db.add(new_procurement)
    db.commit()
    db.refresh(new_procurement)
    return new_procurement


@router.get("/", response_model=list[ProcurementResponse])
def get_procurements(db: Session = Depends(get_db)):
    return db.query(Procurement).all()


@router.get("/{procurement_id}", response_model=ProcurementResponse)
def get_procurement(procurement_id: int, db: Session = Depends(get_db)):
    procurement = db.query(Procurement).filter(Procurement.id == procurement_id).first()

    if not procurement:
        raise HTTPException(status_code=404, detail="Procurement not found")

    return procurement


@router.put("/{procurement_id}", response_model=ProcurementResponse)
def update_procurement(procurement_id: int, data: ProcurementCreate, db: Session = Depends(get_db)):
    procurement = db.query(Procurement).filter(Procurement.id == procurement_id).first()

    if not procurement:
        raise HTTPException(status_code=404, detail="Procurement not found")

    for key, value in data.model_dump().items():
        setattr(procurement, key, value)

    db.commit()
    db.refresh(procurement)

    return procurement


@router.delete("/{procurement_id}")
def delete_procurement(procurement_id: int, db: Session = Depends(get_db)):
    procurement = db.query(Procurement).filter(Procurement.id == procurement_id).first()

    if not procurement:
        raise HTTPException(status_code=404, detail="Procurement not found")

    db.delete(procurement)
    db.commit()

    return {"message": "Procurement deleted successfully"}