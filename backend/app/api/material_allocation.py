from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal

from app.models.material_allocation import MaterialAllocation
from app.models.material import Material
from app.models.inventory import Inventory
from app.models.project import Project
from app.models.stock_movement import StockMovement

from app.schemas.material_allocation_schema import (
    MaterialAllocationCreate,
    MaterialAllocationResponse
)


router = APIRouter(
    prefix="/material-allocations",
    tags=["Material Allocations"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=MaterialAllocationResponse
)
def allocate_material(
    allocation: MaterialAllocationCreate,
    db: Session = Depends(get_db)
):

    # -----------------------------
    # Validate quantity
    # -----------------------------
    if allocation.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    # -----------------------------
    # Check project
    # -----------------------------
    project = db.query(Project).filter(
        Project.id == allocation.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------
    # Check material
    # -----------------------------
    material = db.query(Material).filter(
        Material.id == allocation.material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    # -----------------------------
    # Check approved material request
    # -----------------------------
    from app.models.material_request import MaterialRequest

    approved_request = db.query(MaterialRequest).filter(
        MaterialRequest.project_id == allocation.project_id,
        MaterialRequest.material_id == allocation.material_id,
        MaterialRequest.status == "Approved"
    ).first()

    if not approved_request:
        raise HTTPException(
            status_code=400,
            detail="No approved material request exists for this project and material"
        )

    # -----------------------------
    # Make sure allocation does not
    # exceed approved request
    # -----------------------------
    existing_allocated = db.query(
        MaterialAllocation
    ).filter(
        MaterialAllocation.project_id == allocation.project_id,
        MaterialAllocation.material_id == allocation.material_id,
        MaterialAllocation.status == "ALLOCATED"
    ).all()

    already_allocated = sum(
        item.quantity for item in existing_allocated
    )

    remaining_requested = (
        approved_request.quantity - already_allocated
    )

    if allocation.quantity > remaining_requested:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Allocation exceeds approved request. "
                f"Remaining approved quantity: {remaining_requested}"
            )
        )

    # -----------------------------
    # Find central inventory
    # -----------------------------
    inventory = db.query(Inventory).filter(
        Inventory.item_name == material.name,
        Inventory.project_id.is_(None)
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Material is not available in central inventory"
        )

    # -----------------------------
    # Check available stock
    # -----------------------------
    if inventory.quantity < allocation.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {inventory.quantity}"
        )

    # -----------------------------
    # Reduce available stock
    # -----------------------------
    inventory.quantity -= allocation.quantity

    # -----------------------------
    # Create allocation
    # -----------------------------
    new_allocation = MaterialAllocation(
        project_id=allocation.project_id,
        material_id=allocation.material_id,
        quantity=allocation.quantity,
        allocation_date=allocation.allocation_date,
        work_activity=allocation.work_activity,
        responsible_user=allocation.responsible_user,
        status="ALLOCATED"
    )

    db.add(new_allocation)

    # -----------------------------
    # Create stock movement
    # -----------------------------
    movement = StockMovement(
        material_id=allocation.material_id,
        project_id=allocation.project_id,
        movement_type="ALLOCATED",
        quantity=allocation.quantity,
        remarks=allocation.work_activity
    )

    db.add(movement)

    db.commit()

    db.refresh(new_allocation)

    return new_allocation


# ============================================================
# CONSUME MATERIAL
# ============================================================

@router.post(
    "/{allocation_id}/consume",
    response_model=MaterialAllocationResponse
)
def consume_material(
    allocation_id: int,
    db: Session = Depends(get_db)
):

    # -----------------------------
    # Find allocation
    # -----------------------------
    allocation = db.query(
        MaterialAllocation
    ).filter(
        MaterialAllocation.id == allocation_id
    ).first()

    if not allocation:
        raise HTTPException(
            status_code=404,
            detail="Material allocation not found"
        )

    # -----------------------------
    # Check allocation status
    # -----------------------------
    if allocation.status == "CONSUMED":
        raise HTTPException(
            status_code=400,
            detail="This material allocation has already been consumed"
        )

    # -----------------------------
    # Find material
    # -----------------------------
    material = db.query(Material).filter(
        Material.id == allocation.material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    # -----------------------------
    # Change allocation status
    # -----------------------------
    allocation.status = "CONSUMED"

    # -----------------------------
    # Record consumption movement
    # -----------------------------
    movement = StockMovement(
        material_id=allocation.material_id,
        project_id=allocation.project_id,
        movement_type="CONSUMED",
        quantity=allocation.quantity,
        remarks=f"Consumed for {allocation.work_activity}"
    )

    db.add(movement)

    db.commit()

    db.refresh(allocation)

    return allocation