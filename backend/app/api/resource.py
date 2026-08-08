
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resource import Resource
from app.schemas.resource_schema import (
    ResourceCreate,
    ResourceResponse,
    ResourceAllocation,
    ResourceUtilization
)

router = APIRouter(
    prefix="/resources",
    tags=["Resources"]
)


# =========================================================
# Create Resource
# =========================================================

@router.post("/", response_model=ResourceResponse)
def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    # Validate quantity
    if resource.quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Resource quantity cannot be negative"
        )

    new_resource = Resource(
        name=resource.name,
        type=resource.type,
        quantity=resource.quantity,
        allocated_quantity=0,
        status=resource.status,
        project_id=resource.project_id
    )

    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return new_resource


# =========================================================
# Get All Resources
# =========================================================

@router.get("/", response_model=list[ResourceResponse])
def get_resources(
    db: Session = Depends(get_db)
):
    return db.query(Resource).all()


# =========================================================
# Get Resource By ID
# =========================================================

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    return resource


# =========================================================
# Update Resource
# =========================================================

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_data: ResourceCreate,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # Do not allow total quantity to become
    # smaller than currently allocated quantity
    if resource_data.quantity < resource.allocated_quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                "Total quantity cannot be less than "
                "allocated quantity"
            )
        )

    resource.name = resource_data.name
    resource.type = resource_data.type
    resource.quantity = resource_data.quantity
    resource.status = resource_data.status
    resource.project_id = resource_data.project_id

    db.commit()
    db.refresh(resource)

    return resource


# =========================================================
# Allocate Resource
# =========================================================

@router.put(
    "/{resource_id}/allocate",
    response_model=ResourceResponse
)
def allocate_resource(
    resource_id: int,
    allocation: ResourceAllocation,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    available_quantity = (
        resource.quantity - resource.allocated_quantity
    )

    # Check availability
    if allocation.quantity > available_quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Insufficient resource availability. "
                f"Available quantity: {available_quantity}"
            )
        )

    resource.allocated_quantity += allocation.quantity

    # Update status
    if resource.allocated_quantity == resource.quantity:
        resource.status = "Fully Allocated"
    elif resource.allocated_quantity > 0:
        resource.status = "Partially Allocated"
    else:
        resource.status = "Available"

    db.commit()
    db.refresh(resource)

    return resource


# =========================================================
# Release Resource
# =========================================================

@router.put(
    "/{resource_id}/release",
    response_model=ResourceResponse
)
def release_resource(
    resource_id: int,
    allocation: ResourceAllocation,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # Cannot release more than allocated
    if allocation.quantity > resource.allocated_quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot release {allocation.quantity}. "
                f"Currently allocated: "
                f"{resource.allocated_quantity}"
            )
        )

    resource.allocated_quantity -= allocation.quantity

    # Update status
    if resource.allocated_quantity == 0:
        resource.status = "Available"
    elif resource.allocated_quantity < resource.quantity:
        resource.status = "Partially Allocated"
    else:
        resource.status = "Fully Allocated"

    db.commit()
    db.refresh(resource)

    return resource


# =========================================================
# Resource Utilization
# =========================================================

@router.get(
    "/{resource_id}/utilization",
    response_model=ResourceUtilization
)
def get_resource_utilization(
    resource_id: int,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    total_quantity = resource.quantity
    allocated_quantity = resource.allocated_quantity

    available_quantity = (
        total_quantity - allocated_quantity
    )

    # Calculate utilization percentage
    if total_quantity > 0:
        utilization_percentage = round(
            (allocated_quantity / total_quantity) * 100,
            2
        )
    else:
        utilization_percentage = 0.0

    return {
        "resource_id": resource.id,
        "resource_name": resource.name,
        "total_quantity": total_quantity,
        "allocated_quantity": allocated_quantity,
        "available_quantity": available_quantity,
        "utilization_percentage": utilization_percentage,
        "status": resource.status
    }


# =========================================================
# Delete Resource
# =========================================================

@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # Prevent deletion of allocated resources
    if resource.allocated_quantity > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Resource cannot be deleted while "
                "it is allocated"
            )
        )

    db.delete(resource)
    db.commit()

    return {
        "message": "Resource deleted successfully"}
