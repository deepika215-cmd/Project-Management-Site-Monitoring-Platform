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


# ============================================================
# GET ALL INVENTORY
# ============================================================

@router.get(
    "/",
    response_model=list[InventoryResponse]
)
def get_inventory(
    db: Session = Depends(get_db)
):
    return db.query(Inventory).all()


# ============================================================
# INVENTORY STATUS
# ============================================================

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

        if not material:
            continue

        minimum_stock = material.minimum_stock or 0

        # ----------------------------------------------------
        # Current available central stock
        # ----------------------------------------------------

        available_stock = inventory.quantity

        # ----------------------------------------------------
        # Total allocated movements
        # ----------------------------------------------------

        allocated_result = db.query(
            StockMovement
        ).filter(
            StockMovement.material_id == material.id,
            StockMovement.movement_type == "ALLOCATED"
        ).all()

        total_allocated = sum(
            movement.quantity
            for movement in allocated_result
        )

        # ----------------------------------------------------
        # Total consumed movements
        # ----------------------------------------------------

        consumed_result = db.query(
            StockMovement
        ).filter(
            StockMovement.material_id == material.id,
            StockMovement.movement_type == "CONSUMED"
        ).all()

        total_consumed = sum(
            movement.quantity
            for movement in consumed_result
        )

        # ----------------------------------------------------
        # Allocated but not consumed
        # ----------------------------------------------------

        allocated_stock = max(
            total_allocated - total_consumed,
            0
        )

        # ----------------------------------------------------
        # Total stock handled by system
        # ----------------------------------------------------

        total_stock = (
            available_stock
            + allocated_stock
            + total_consumed
        )

        # ----------------------------------------------------
        # Stock status
        # ----------------------------------------------------

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