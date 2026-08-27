from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.purchase_order import PurchaseOrder
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.material import Material
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.user import User

from app.schemas.purchase_order_schema import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
)

from app.core.permissions import role_required


router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"],
)


# ============================================================
# CREATE PURCHASE ORDER
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.post(
    "/",
    response_model=PurchaseOrderResponse,
)
def create_purchase_order(
    purchase_order: PurchaseOrderCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):
    request = (
        db.query(ProcurementRequest)
        .filter(
            ProcurementRequest.id
            == purchase_order.procurement_request_id
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Procurement request not found",
        )

    if request.status != "Approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Purchase order can only be created "
                "for an approved procurement request"
            ),
        )

    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == purchase_order.vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    new_purchase_order = PurchaseOrder(
        **purchase_order.model_dump()
    )

    db.add(new_purchase_order)
    db.commit()
    db.refresh(new_purchase_order)

    request.status = "Processing"
    db.commit()

    return new_purchase_order


# ============================================================
# GET ALL PURCHASE ORDERS
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[PurchaseOrderResponse],
)
def get_purchase_orders(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(PurchaseOrder).all()


# ============================================================
# GET PURCHASE ORDER BY ID
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse,
)
def get_purchase_order(
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
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    return purchase_order


# ============================================================
# UPDATE PURCHASE ORDER
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{purchase_order_id}",
    response_model=PurchaseOrderResponse,
)
def update_purchase_order(
    purchase_order_id: int,
    purchase_order_data: PurchaseOrderCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    for key, value in purchase_order_data.model_dump().items():
        setattr(purchase_order, key, value)

    db.commit()
    db.refresh(purchase_order)

    return purchase_order


# ============================================================
# COMPLETE PURCHASE ORDER
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{purchase_order_id}/complete",
    response_model=PurchaseOrderResponse,
)
def complete_purchase_order(
    purchase_order_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    if purchase_order.status != "Processing":
        raise HTTPException(
            status_code=400,
            detail="Only processing purchase orders can be completed",
        )

    purchase_order.status = "Completed"

    request = (
        db.query(ProcurementRequest)
        .filter(
            ProcurementRequest.id
            == purchase_order.procurement_request_id
        )
        .first()
    )

    if request:
        request.status = "Completed"

    db.commit()
    db.refresh(purchase_order)

    return purchase_order


# ============================================================
# RECEIVE PURCHASE ORDER
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
#
# This is the Module 5 integration:
#
# PO
#  ↓
# Material
#  ↓
# Inventory + quantity
#  ↓
# StockMovement RECEIVED
#  ↓
# PO Completed
#  ↓
# Procurement Request Completed
# ============================================================

@router.put(
    "/{purchase_order_id}/receive",
    response_model=PurchaseOrderResponse,
)
def receive_purchase_order(
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
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    if purchase_order.status != "Processing":
        raise HTTPException(
            status_code=400,
            detail="Only processing purchase orders can be received",
        )

    purchase_order_items = (
        db.query(PurchaseOrderItem)
        .filter(
            PurchaseOrderItem.purchase_order_id
            == purchase_order_id
        )
        .all()
    )

    if not purchase_order_items:
        raise HTTPException(
            status_code=400,
            detail="Purchase order has no items",
        )

    for item in purchase_order_items:

        material = (
            db.query(Material)
            .filter(Material.name == item.item_name)
            .first()
        )

        if not material:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Material '{item.item_name}' "
                    "not found in materials"
                ),
            )

        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.item_name == material.name,
                Inventory.project_id.is_(None),
            )
            .first()
        )

        if not inventory:
            inventory = Inventory(
                item_name=material.name,
                category=material.category,
                quantity=0,
                unit=material.unit,
                project_id=None,
            )

            db.add(inventory)
            db.flush()

        inventory.quantity += item.quantity

        stock_movement = StockMovement(
            material_id=material.id,
            project_id=None,
            movement_type="RECEIVED",
            quantity=item.quantity,
            remarks=(
                f"Received from Purchase Order "
                f"#{purchase_order.id}"
            ),
        )

        db.add(stock_movement)

    purchase_order.status = "Completed"

    request = (
        db.query(ProcurementRequest)
        .filter(
            ProcurementRequest.id
            == purchase_order.procurement_request_id
        )
        .first()
    )

    if request:
        request.status = "Completed"

    db.commit()
    db.refresh(purchase_order)

    return purchase_order


# ============================================================
# DELETE PURCHASE ORDER
# Allowed: ADMIN only
# ============================================================

@router.delete("/{purchase_order_id}")
def delete_purchase_order(
    purchase_order_id: int,
    current_user: User = Depends(
        role_required(["ADMIN"])
    ),
    db: Session = Depends(get_db),
):
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    db.delete(purchase_order)
    db.commit()

    return {
        "message": "Purchase order deleted successfully"
    }