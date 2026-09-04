from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resource import Resource
from app.models.project import Project
from app.models.worker import Worker
from app.models.resource_allocation import ResourceAllocation
from app.schemas.resource_allocation_schema import (
    ResourceAllocationCreate,
    ResourceAllocationResponse
)

router = APIRouter(
    prefix="/resource-allocations",
    tags=["Resource Allocations"]
)


@router.post(
    "/",
    response_model=ResourceAllocationResponse
)
def create_resource_allocation(
    allocation: ResourceAllocationCreate,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(
        Resource.id == allocation.resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    project = db.query(Project).filter(
        Project.id == allocation.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    worker = db.query(Worker).filter(
        Worker.id == allocation.worker_id
    ).first()

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    if allocation.expected_return_date < allocation.allocation_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "Expected return date cannot be before "
                "allocation date"
            )
        )

    overlapping_allocations = db.query(
        ResourceAllocation
    ).filter(
        ResourceAllocation.resource_id == allocation.resource_id,
        ResourceAllocation.status == "Allocated",
        ResourceAllocation.allocation_date
        <= allocation.expected_return_date,
        ResourceAllocation.expected_return_date
        >= allocation.allocation_date
    ).all()

    allocated_during_period = sum(
        record.quantity
        for record in overlapping_allocations
    )

    available_quantity = (
        resource.quantity - allocated_during_period
    )

    if allocation.quantity > available_quantity:
        raise HTTPException(
            status_code=400,
            detail=(
                "Insufficient resource availability for "
                "the selected period. "
                f"Available quantity: {available_quantity}"
            )
        )

    new_allocation = ResourceAllocation(
        resource_id=allocation.resource_id,
        project_id=allocation.project_id,
        worker_id=allocation.worker_id,
        quantity=allocation.quantity,
        allocation_date=allocation.allocation_date,
        expected_return_date=allocation.expected_return_date,
        responsible_person=worker.name,
        status="Allocated"
    )

    db.add(new_allocation)

    today = date.today()

    if (
        allocation.allocation_date <= today
        <= allocation.expected_return_date
    ):
        resource.allocated_quantity += allocation.quantity

        if resource.allocated_quantity >= resource.quantity:
            resource.status = "Fully Allocated"
        elif resource.allocated_quantity > 0:
            resource.status = "Partially Allocated"
        else:
            resource.status = "Available"

    db.commit()
    db.refresh(new_allocation)

    return new_allocation


@router.get(
    "/",
    response_model=list[ResourceAllocationResponse]
)
def get_resource_allocations(
    db: Session = Depends(get_db)
):
    return db.query(ResourceAllocation).all()


@router.get(
    "/{allocation_id}",
    response_model=ResourceAllocationResponse
)
def get_resource_allocation(
    allocation_id: int,
    db: Session = Depends(get_db)
):
    allocation = db.query(
        ResourceAllocation
    ).filter(
        ResourceAllocation.id == allocation_id
    ).first()

    if not allocation:
        raise HTTPException(
            status_code=404,
            detail="Resource allocation not found"
        )

    return allocation


@router.put(
    "/{allocation_id}/return",
    response_model=ResourceAllocationResponse
)
def return_resource_allocation(
    allocation_id: int,
    db: Session = Depends(get_db)
):
    allocation = db.query(
        ResourceAllocation
    ).filter(
        ResourceAllocation.id == allocation_id
    ).first()

    if not allocation:
        raise HTTPException(
            status_code=404,
            detail="Resource allocation not found"
        )

    if allocation.status != "Allocated":
        raise HTTPException(
            status_code=400,
            detail=(
                "Resource allocation is already "
                "returned or not active"
            )
        )

    resource = db.query(Resource).filter(
        Resource.id == allocation.resource_id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    allocation.actual_return_date = date.today()
    allocation.status = "Returned"

    resource.allocated_quantity = max(
        0,
        resource.allocated_quantity - allocation.quantity
    )

    if resource.allocated_quantity == 0:
        resource.status = "Available"
    elif resource.allocated_quantity >= resource.quantity:
        resource.status = "Fully Allocated"
    else:
        resource.status = "Partially Allocated"

    db.commit()
    db.refresh(allocation)

    return allocation