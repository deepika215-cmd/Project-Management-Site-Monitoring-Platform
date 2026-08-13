from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.stock_movement import StockMovement
from app.models.material import Material
from app.models.inventory import Inventory

from app.schemas.stock_movement_schema import (
    StockMovementCreate,
    StockMovementResponse
)


router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=StockMovementResponse)
def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db)
):

    if movement.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    material = db.query(Material).filter(
        Material.id == movement.material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    inventory = db.query(Inventory).filter(
        Inventory.item_name == material.name,
        Inventory.project_id.is_(None)
    ).first()

    if not inventory:

        inventory = Inventory(
            item_name=material.name,
            category=material.category,
            quantity=0,
            unit=material.unit,
            project_id=None
        )

        db.add(inventory)
        db.flush()

    movement_type = movement.movement_type.upper()

    if movement_type == "RECEIVED":

        inventory.quantity += movement.quantity

    elif movement_type == "CONSUMED":

        if inventory.quantity < movement.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {inventory.quantity}"
            )

        inventory.quantity -= movement.quantity

    else:
        raise HTTPException(
            status_code=400,
            detail="movement_type must be RECEIVED or CONSUMED"
        )

    new_movement = StockMovement(
        material_id=movement.material_id,
        project_id=movement.project_id,
        movement_type=movement_type,
        quantity=movement.quantity,
        remarks=movement.remarks
    )

    db.add(new_movement)

    db.commit()
    db.refresh(new_movement)

    return new_movement


@router.get("/", response_model=list[StockMovementResponse])
def get_stock_movements(
    db: Session = Depends(get_db)
):
    return db.query(StockMovement).all()
