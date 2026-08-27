from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.vendor import Vendor
from app.models.user import User
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem

from app.schemas.vendor_schema import (
    VendorCreate,
    VendorResponse,
)

from app.core.permissions import role_required


router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"],
)

# ============================================================
# GET SUPPLIER PROCUREMENT HISTORY
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{vendor_id}/procurement-history",
)
def get_supplier_procurement_history(
    vendor_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    purchase_orders = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.vendor_id == vendor_id
        )
        .all()
    )

    return [
        {
            "purchase_order_id": po.id,
            "project_id": po.project_id,
            "procurement_request_id": po.procurement_request_id,
            "order_date": po.order_date,
            "expected_delivery_date": po.expected_delivery_date,
            "overall_amount": po.overall_amount,
            "status": po.status,
        }
        for po in purchase_orders
    ]
# ============================================================
# CREATE SUPPLIER / VENDOR
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.post(
    "/",
    response_model=VendorResponse,
)
def create_vendor(
    vendor: VendorCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    existing = (
        db.query(Vendor)
        .filter(
            Vendor.vendor_name == vendor.vendor_name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Vendor already exists",
        )

    new_vendor = Vendor(
        **vendor.model_dump()
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor


# ============================================================
# GET ALL SUPPLIERS / VENDORS
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[VendorResponse],
)
def get_vendors(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(Vendor).all()


# ============================================================
# GET ACTIVE SUPPLIERS
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/active",
    response_model=list[VendorResponse],
)
def get_active_vendors(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(Vendor).filter(
        Vendor.status == "ACTIVE"
    ).all()


# ============================================================
# GET SUPPLIERS BY CATEGORY
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/category/{category}",
    response_model=list[VendorResponse],
)
def get_vendors_by_category(
    category: str,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(Vendor).filter(
        Vendor.category == category
    ).all()


# ============================================================
# GET SUPPLIER / VENDOR BY ID
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
)
def get_vendor(
    vendor_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    return vendor


# ============================================================
# UPDATE SUPPLIER / VENDOR
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
)
def update_vendor(
    vendor_id: int,
    vendor_data: VendorCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    duplicate = (
        db.query(Vendor)
        .filter(
            Vendor.vendor_name == vendor_data.vendor_name,
            Vendor.id != vendor_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another vendor with this name already exists",
        )

    for key, value in vendor_data.model_dump().items():
        setattr(vendor, key, value)

    db.commit()
    db.refresh(vendor)

    return vendor


# ============================================================
# DELETE SUPPLIER / VENDOR
# Allowed: ADMIN
# ============================================================

@router.delete("/{vendor_id}")
def delete_vendor(
    vendor_id: int,
    current_user: User = Depends(
        role_required(["ADMIN"])
    ),
    db: Session = Depends(get_db),
):

    vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    db.delete(vendor)
    db.commit()

    return {
        "message": "Vendor deleted successfully"
    }