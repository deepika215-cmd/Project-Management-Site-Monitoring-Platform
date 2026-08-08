from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.inventory import Inventory
from app.schemas.inventory_schema import (
    InventoryCreate,
    InventoryResponse,
    InventoryUsage,
    InventoryUtilization
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


# ============================================================
# Create Inventory
# ============================================================

@router.post("/", response_model=InventoryResponse)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):
    new_inventory = Inventory(**inventory.model_dump())

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory


# ============================================================
# Get All Inventory
# ============================================================

@router.get("/", response_model=list[InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db)
):
    return db.query(Inventory).all()


# ============================================================
# Get Inventory By ID
# ============================================================

@router.get("/{inventory_id}", response_model=InventoryResponse)
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
            detail="Inventory not found"
        )

    return inventory


# ============================================================
# Update Inventory
# ============================================================

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found"
        )

    for key, value in inventory_data.model_dump().items():
        setattr(inventory, key, value)

    db.commit()
    db.refresh(inventory)

    return inventory


# ============================================================
# Delete Inventory
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
            detail="Inventory not found"
        )

    db.delete(inventory)
    db.commit()

    return {
        "message": "Inventory deleted successfully"
    }


# ============================================================
# Use Inventory
# ============================================================

@router.put("/{inventory_id}/use", response_model=InventoryResponse)
def use_inventory(
    inventory_id: int,
    usage: InventoryUsage,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found"
        )

    available_quantity = inventory.quantity - inventory.used

    if usage.quantity > available_quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough inventory available"
        )

    inventory.used += usage.quantity

    if inventory.used == inventory.quantity:
        inventory.status = "Out of Stock"
    else:
        inventory.status = "Available"

    db.commit()
    db.refresh(inventory)

    return inventory


# ============================================================
# Release Inventory
# ============================================================

@router.put("/{inventory_id}/release", response_model=InventoryResponse)
def release_inventory(
    inventory_id: int,
    usage: InventoryUsage,
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory not found"
        )

    if usage.quantity > inventory.used:
        raise HTTPException(
            status_code=400,
            detail="Cannot release more inventory than currently used"
        )

    inventory.used -= usage.quantity

    if inventory.used < inventory.quantity:
        inventory.status = "Available"

    db.commit()
    db.refresh(inventory)

    return inventory


# ============================================================
# Get Inventory Utilization
# ============================================================

@router.get(
    "/{inventory_id}/utilization",
    response_model=InventoryUtilization
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
            detail="Inventory not found"
        )

    available_quantity = inventory.quantity - inventory.used

    if inventory.quantity > 0:
        utilization_percentage = (
            inventory.used / inventory.quantity
        ) * 100
    else:
        utilization_percentage = 0

    return {
        "inventory_id": inventory.id,
        "material_name": inventory.material_name,
        "total_quantity": inventory.quantity,
        "used_quantity": inventory.used,
        "available_quantity": available_quantity,
        "utilization_percentage": round(
            utilization_percentage,
            2
        ),
        "status": inventory.status
    }

