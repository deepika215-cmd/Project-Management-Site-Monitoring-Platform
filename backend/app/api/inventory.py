from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.inventory import Inventory
from app.models.material import Material
from app.models.stock_movement import StockMovement

from app.schemas.inventory_schema import (
    InventoryResponse,
    InventoryStatusResponse
)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=list[InventoryResponse]
)
def get_inventory(
    db: Session = Depends(get_db)
):
    return db.query(Inventory).all()


@router.get(
    "/status",
    response_model=list[InventoryStatusResponse]
)
def get_inventory_status(
    db: Session = Depends(get_db)
):

    inventory_items = db.query(Inventory).filter(
        Inventory.project_id.is_(None)
    ).all()

    result = []

    for inventory in inventory_items:

        material = db.query(Material).filter(
            Material.name == inventory.item_name
        ).first()

        minimum_stock = material.minimum_stock if material else 0

        # Total quantity currently present in central inventory
        total_stock = inventory.quantity

        # Calculate allocated quantity that has not yet been consumed
        allocated_result = db.query(
            StockMovement
        ).filter(
            StockMovement.material_id == material.id,
            StockMovement.movement_type == "ALLOCATED"
        ).all()

        consumed_result = db.query(
            StockMovement
        ).filter(
            StockMovement.material_id == material.id,
            StockMovement.movement_type == "CONSUMED"
        ).all()

        total_allocated = sum(
            movement.quantity
            for movement in allocated_result
        )

        total_consumed = sum(
            movement.quantity
            for movement in consumed_result
        )

        # Allocated but not yet consumed
        allocated_stock = total_allocated - total_consumed

        if allocated_stock < 0:
            allocated_stock = 0

        # Central inventory quantity is already the available stock.
        available_stock = total_stock

        if available_stock == 0:
            status = "OUT_OF_STOCK"

        elif available_stock <= minimum_stock:
            status = "LOW_STOCK"

        else:
            status = "AVAILABLE"

        result.append(
            InventoryStatusResponse(
                id=inventory.id,
                item_name=inventory.item_name,
                category=inventory.category,
                total_stock=total_stock,
                allocated_stock=allocated_stock,
                consumed_stock=total_consumed,
                available_stock=available_stock,
                unit=inventory.unit,
                minimum_stock=minimum_stock,
                available_status=status
            )
        )

    return result