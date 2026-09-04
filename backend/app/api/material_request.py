from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.material_request import MaterialRequest
from app.models.material import Material
from app.models.project import Project
from app.models.material_allocation import MaterialAllocation

from app.schemas.material_request_schema import (
    MaterialRequestCreate,
    MaterialRequestResponse
)

router = APIRouter(
    prefix="/material-requests",
    tags=["Material Requests"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# CREATE MATERIAL REQUEST
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=MaterialRequestResponse
)
def create_material_request(
    request: MaterialRequestCreate,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == request.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    material = db.query(Material).filter(
        Material.id == request.material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    new_request = MaterialRequest(
        project_id=request.project_id,
        material_id=request.material_id,
        quantity=request.quantity,
        required_date=request.required_date,
        purpose=request.purpose,
        remarks=request.remarks,
        status="Pending"
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


# ---------------------------------------------------------
# GET ALL MATERIAL REQUESTS
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[MaterialRequestResponse]
)
def get_material_requests(
    db: Session = Depends(get_db)
):

    return db.query(MaterialRequest).all()


# ---------------------------------------------------------
# APPROVE MATERIAL REQUEST
# ---------------------------------------------------------

@router.put(
    "/{request_id}/approve",
    response_model=MaterialRequestResponse
)
def approve_material_request(
    request_id: int,
    db: Session = Depends(get_db)
):

    material_request = db.query(MaterialRequest).filter(
        MaterialRequest.id == request_id
    ).first()

    if not material_request:
        raise HTTPException(
            status_code=404,
            detail="Material request not found"
        )

    if material_request.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=(
                "Request cannot be approved because "
                f"its current status is {material_request.status}"
            )
        )

    material_request.status = "Approved"

    db.commit()
    db.refresh(material_request)

    return material_request


# ---------------------------------------------------------
# REJECT MATERIAL REQUEST
# ---------------------------------------------------------

@router.put(
    "/{request_id}/reject",
    response_model=MaterialRequestResponse
)
def reject_material_request(
    request_id: int,
    db: Session = Depends(get_db)
):

    material_request = db.query(MaterialRequest).filter(
        MaterialRequest.id == request_id
    ).first()

    if not material_request:
        raise HTTPException(
            status_code=404,
            detail="Material request not found"
        )

    if material_request.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=(
                "Request cannot be rejected because "
                f"its current status is {material_request.status}"
            )
        )

    material_request.status = "Rejected"

    db.commit()
    db.refresh(material_request)

    return material_request


# ---------------------------------------------------------
# FULFILL MATERIAL REQUEST
# ---------------------------------------------------------

@router.put(
    "/{request_id}/fulfill",
    response_model=MaterialRequestResponse
)
def fulfill_material_request(
    request_id: int,
    db: Session = Depends(get_db)
):

    material_request = db.query(MaterialRequest).filter(
        MaterialRequest.id == request_id
    ).first()

    if not material_request:
        raise HTTPException(
            status_code=404,
            detail="Material request not found"
        )

    # Request must be approved first
    if material_request.status != "Approved":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only an Approved material request "
                "can be fulfilled"
            )
        )

    # Find allocations made for this request's
    # project and material
    allocations = db.query(MaterialAllocation).filter(
        MaterialAllocation.project_id == material_request.project_id,
        MaterialAllocation.material_id == material_request.material_id
    ).all()

    total_allocated = sum(
        allocation.quantity
        for allocation in allocations
    )

    # Make sure enough material has been allocated
    if total_allocated < material_request.quantity:

        remaining = (
            material_request.quantity - total_allocated
        )

        raise HTTPException(
            status_code=400,
            detail=(
                f"Request cannot be fulfilled. "
                f"Required: {material_request.quantity}, "
                f"Allocated: {total_allocated}, "
                f"Remaining: {remaining}"
            )
        )

    # Request is completely fulfilled
    material_request.status = "Fulfilled"

    db.commit()
    db.refresh(material_request)

    return material_request