from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.purchase_order import PurchaseOrder
from app.models.user import User

from app.schemas.purchase_order_item_schema import (
    PurchaseOrderItemCreate,
    PurchaseOrderItemResponse,
)

from app.core.permissions import role_required


router = APIRouter(
    prefix="/purchase-order-items",
    tags=["Purchase Order Items"],
)


# ============================================================
# CREATE PURCHASE ORDER ITEM
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.post(
    "/",
    response_model=PurchaseOrderItemResponse,
)
def create_purchase_order_item(
    item: PurchaseOrderItemCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    # Check purchase order exists
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == item.purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    # Items cannot be added after PO completion
    if purchase_order.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Cannot add items to a completed purchase order",
        )

    # Validate quantity
    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    # Validate unit price
    if item.unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Unit price cannot be negative",
        )

    # Calculate total price
    total_price = item.quantity * item.unit_price

    new_item = PurchaseOrderItem(
        purchase_order_id=item.purchase_order_id,
        item_name=item.item_name,
        category=item.category,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=total_price,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# ============================================================
# GET ALL PURCHASE ORDER ITEMS
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[PurchaseOrderItemResponse],
)
def get_purchase_order_items(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    return (
        db.query(PurchaseOrderItem)
        .all()
    )


# ============================================================
# GET ITEMS FOR SPECIFIC PURCHASE ORDER
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/order/{purchase_order_id}",
    response_model=list[PurchaseOrderItemResponse],
)
def get_items_for_purchase_order(
    purchase_order_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    # Check purchase order exists
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    return (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.purchase_order_id
            == purchase_order_id
        )
        .all()
    )


# ============================================================
# GET PURCHASE ORDER ITEM BY ID
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{item_id}",
    response_model=PurchaseOrderItemResponse,
)
def get_purchase_order_item(
    item_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    item = (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.id == item_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Purchase order item not found",
        )

    return item


# ============================================================
# UPDATE PURCHASE ORDER ITEM
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{item_id}",
    response_model=PurchaseOrderItemResponse,
)
def update_purchase_order_item(
    item_id: int,
    item_data: PurchaseOrderItemCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    item = (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.id == item_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Purchase order item not found",
        )

    # Check target purchase order
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id
            == item.purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    if purchase_order.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Cannot update items of a completed purchase order",
        )

    if item_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    if item_data.unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Unit price cannot be negative",
        )

    item.item_name = item_data.item_name
    item.category = item_data.category
    item.quantity = item_data.quantity
    item.unit_price = item_data.unit_price

    item.total_price = (
        item_data.quantity
        * item_data.unit_price
    )

    db.commit()
    db.refresh(item)

    return item


# ============================================================
# DELETE PURCHASE ORDER ITEM
# Allowed: ADMIN
# ============================================================

@router.delete("/{item_id}")
def delete_purchase_order_item(
    item_id: int,
    current_user: User = Depends(
        role_required(["ADMIN"])
    ),
    db: Session = Depends(get_db),
):

    item = (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.id == item_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Purchase order item not found",
        )

    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id
            == item.purchase_order_id
        )
        .first()
    )

    if purchase_order and purchase_order.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete items from a completed purchase order",
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Purchase order item deleted successfully"
    }