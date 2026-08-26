from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.procurement_request_item import ProcurementRequestItem
from app.models.procurement_request import ProcurementRequest
from app.models.user import User

from app.schemas.procurement_request_item_schema import (
    ProcurementRequestItemCreate,
    ProcurementRequestItemResponse,
)

from app.core.permissions import role_required


router = APIRouter(
    prefix="/procurement-request-items",
    tags=["Procurement Request Items"],
)


# ============================================================
# CREATE PROCUREMENT REQUEST ITEM
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.post(
    "/",
    response_model=ProcurementRequestItemResponse,
)
def create_procurement_request_item(
    item: ProcurementRequestItemCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    request = (
        db.query(ProcurementRequest)
        .filter(
            ProcurementRequest.id
            == item.procurement_request_id
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Procurement request not found",
        )

    if request.status in ["Rejected", "Completed"]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Items cannot be added to a "
                "rejected or completed procurement request"
            ),
        )

    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    if item.estimated_unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Estimated unit price cannot be negative",
        )

    total_price = (
        item.quantity * item.estimated_unit_price
    )

    new_item = ProcurementRequestItem(
        procurement_request_id=item.procurement_request_id,
        item_name=item.item_name,
        category=item.category,
        quantity=item.quantity,
        estimated_unit_price=item.estimated_unit_price,
        estimated_total_price=total_price,
        remarks=item.remarks,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# ============================================================
# GET ALL PROCUREMENT REQUEST ITEMS
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[ProcurementRequestItemResponse],
)
def get_procurement_request_items(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(
        ProcurementRequestItem
    ).all()


# ============================================================
# GET ITEMS FOR A SPECIFIC PROCUREMENT REQUEST
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/request/{request_id}",
    response_model=list[ProcurementRequestItemResponse],
)
def get_items_for_request(
    request_id: int,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):

    request = (
        db.query(ProcurementRequest)
        .filter(
            ProcurementRequest.id == request_id
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Procurement request not found",
        )

    return db.query(
        ProcurementRequestItem
    ).filter(
        ProcurementRequestItem.procurement_request_id
        == request_id
    ).all()


# ============================================================
# GET ITEM BY ID
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{item_id}",
    response_model=ProcurementRequestItemResponse,
)
def get_procurement_request_item(
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
        db.query(ProcurementRequestItem)
        .filter(
            ProcurementRequestItem.id == item_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Procurement request item not found",
        )

    return item


# ============================================================
# UPDATE PROCUREMENT REQUEST ITEM
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{item_id}",
    response_model=ProcurementRequestItemResponse,
)
def update_procurement_request_item(
    item_id: int,
    item_data: ProcurementRequestItemCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
        ])
    ),
    db: Session = Depends(get_db),
):

    item = (
        db.query(ProcurementRequestItem)
        .filter(
            ProcurementRequestItem.id == item_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Procurement request item not found",
        )

    if item_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    if item_data.estimated_unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail="Estimated unit price cannot be negative",
        )

    item.item_name = item_data.item_name
    item.category = item_data.category
    item.quantity = item_data.quantity
    item.estimated_unit_price = (
        item_data.estimated_unit_price
    )
    item.estimated_total_price = (
        item_data.quantity
        * item_data.estimated_unit_price
    )
    item.remarks = item_data.remarks

    db.commit()
    db.refresh(item)

    return item


# ============================================================
# DELETE PROCUREMENT REQUEST ITEM
# Allowed: ADMIN
# ============================================================

@router.delete("/{item_id}")
def delete_procurement_request_item(
    item_id: int,
    current_user: User = Depends(
        role_required(["ADMIN"])
    ),
    db: Session = Depends(get_db),
):

    item = (
        db.query(ProcurementRequestItem)
        .filter(
            ProcurementRequestItem.id == item_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Procurement request item not found",
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Procurement request item deleted successfully"
    }