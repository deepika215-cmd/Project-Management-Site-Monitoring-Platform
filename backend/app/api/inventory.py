from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.inventory import Inventory
from app.models.material import Material
from app.models.stock_movement import StockMovement

from app.schemas.inventory_schema import (
    InventoryResponse,
    InventoryStatusResponse,
    LowStockAlertResponse
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
# CREATE INVENTORY
# ============================================================

@router.post(
    "/",
    response_model=InventoryResponse
)
def create_inventory(
    inventory_data: dict,
    db: Session = Depends(get_db)
):

    if inventory_data.get("quantity", 0) < 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity cannot be negative"
        )

    new_inventory = Inventory(
        item_name=inventory_data.get("item_name"),
        category=inventory_data.get("category"),
        quantity=inventory_data.get("quantity", 0),
        unit=inventory_data.get("unit"),
        supplier=inventory_data.get("supplier"),
        project_id=inventory_data.get("project_id")
    )

    if not new_inventory.item_name:
        raise HTTPException(
            status_code=400,
            detail="Item name is required"
        )

    if not new_inventory.category:
        raise HTTPException(
            status_code=400,
            detail="Category is required"
        )

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory


# ============================================================
# LOW STOCK ALERT
# ============================================================

@router.get(
    "/low-stock",
    response_model=list[LowStockAlertResponse]
)
def get_low_stock_inventory(
    db: Session = Depends(get_db)
):
    """
    Returns inventory items whose available quantity
    is at or below the material's minimum stock level.
    """

    inventory_items = db.query(Inventory).all()

    result = []

    for inventory in inventory_items:

        material = db.query(Material).filter(
            Material.name == inventory.item_name
        ).first()

        # If no matching material exists,
        # minimum stock information is unavailable.
        if not material:
            continue

        minimum_stock = material.minimum_stock or 0
        available_stock = inventory.quantity or 0

        # Low stock condition
        if available_stock <= minimum_stock:

            if available_stock == 0:
                alert_status = "OUT_OF_STOCK"
                message = (
                    f"{inventory.item_name} is out of stock."
                )
            else:
                alert_status = "LOW_STOCK"
                message = (
                    f"{inventory.item_name} is low in stock. "
                    f"Available: {available_stock}, "
                    f"Minimum required: {minimum_stock}."
                )

            result.append(
                LowStockAlertResponse(
                    id=inventory.id,
                    item_name=inventory.item_name,
                    category=inventory.category,
                    available_stock=available_stock,
                    minimum_stock=minimum_stock,
                    unit=inventory.unit,
                    supplier=inventory.supplier,
                    project_id=inventory.project_id,
                    alert_status=alert_status,
                    message=message
                )
            )

    return result


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

        available_stock = inventory.quantity

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

        allocated_stock = max(
            total_allocated - total_consumed,
            0
        )

        total_stock = (
            available_stock
            + allocated_stock
            + total_consumed
        )

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


# ============================================================
# GET INVENTORY BY ID
# ============================================================

@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def get_inventory_by_id(
    inventory_id: int,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    return inventory


# ============================================================
# UPDATE INVENTORY
# ============================================================

@router.put(
    "/{inventory_id}",
    response_model=InventoryResponse
)
def update_inventory(
    inventory_id: int,
    inventory_data: dict,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    if "quantity" in inventory_data:

        if inventory_data["quantity"] < 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity cannot be negative"
            )

    allowed_fields = [
        "item_name",
        "category",
        "quantity",
        "unit",
        "supplier",
        "project_id"
    ]

    for field in allowed_fields:

        if field in inventory_data:

            setattr(
                inventory,
                field,
                inventory_data[field]
            )

    db.commit()
    db.refresh(inventory)

    return inventory


# ============================================================
# DELETE INVENTORY
# ============================================================

@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    if inventory.quantity > 0:
        raise HTTPException(
            status_code=400,
            detail="Inventory with available stock cannot be deleted"
        )

    db.delete(inventory)
    db.commit()

    return {
        "message": "Inventory item deleted successfully"
    }


# ============================================================
# USE INVENTORY
# ============================================================

@router.put(
    "/{inventory_id}/use",
    response_model=InventoryResponse
)
def use_inventory(
    inventory_id: int,
    data: dict,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    quantity = data.get("quantity")

    if quantity is None or quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if inventory.quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Insufficient stock. "
                f"Available: {inventory.quantity}"
            )
        )

    inventory.quantity -= quantity

    material = db.query(Material).filter(
        Material.name == inventory.item_name
    ).first()

    if material:

        movement = StockMovement(
            material_id=material.id,
            project_id=inventory.project_id,
            movement_type="CONSUMED",
            quantity=quantity,
            remarks=data.get(
                "remarks",
                "Inventory used"
            )
        )

        db.add(movement)

    db.commit()
    db.refresh(inventory)

    return inventory


# ============================================================
# RELEASE INVENTORY
# ============================================================

@router.put(
    "/{inventory_id}/release",
    response_model=InventoryResponse
)
def release_inventory(
    inventory_id: int,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    inventory.quantity += 1

    db.commit()
    db.refresh(inventory)

    return inventory


# ============================================================
# INVENTORY UTILIZATION
# ============================================================

@router.get(
    "/{inventory_id}/utilization"
)
def get_inventory_utilization(
    inventory_id: int,
    db: Session = Depends(get_db)
):

    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )

    material = db.query(Material).filter(
        Material.name == inventory.item_name
    ).first()

    if not material:

        return {
            "inventory_id": inventory.id,
            "item_name": inventory.item_name,
            "available_stock": inventory.quantity,
            "allocated_stock": 0,
            "consumed_stock": 0,
            "utilization_percentage": 0
        }

    allocated = db.query(StockMovement).filter(
        StockMovement.material_id == material.id,
        StockMovement.movement_type == "ALLOCATED"
    ).all()

    consumed = db.query(StockMovement).filter(
        StockMovement.material_id == material.id,
        StockMovement.movement_type == "CONSUMED"
    ).all()

    total_allocated = sum(
        movement.quantity
        for movement in allocated
    )

    total_consumed = sum(
        movement.quantity
        for movement in consumed
    )

    total_handled = (
        inventory.quantity
        + total_allocated
    )

    if total_handled > 0:

        utilization = round(
            (total_consumed / total_handled) * 100,
            2
        )

    else:
        utilization = 0

    return {
        "inventory_id": inventory.id,
        "item_name": inventory.item_name,
        "available_stock": inventory.quantity,
        "allocated_stock": max(
            total_allocated - total_consumed,
            0
        ),
        "consumed_stock": total_consumed,
        "utilization_percentage": utilization
    }