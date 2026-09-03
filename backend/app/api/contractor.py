from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contractor import Contractor
from app.models.project import Project
from app.schemas.contractor_schema import (
    ContractorCreate,
    ContractorResponse,
)


router = APIRouter(
    prefix="/contractors",
    tags=["Contractors"],
)


# ============================================================
# CREATE CONTRACTOR
# ============================================================

@router.post(
    "/",
    response_model=ContractorResponse
)
def create_contractor(
    contractor: ContractorCreate,
    db: Session = Depends(get_db),
):
    new_contractor = Contractor(
        **contractor.model_dump()
    )

    db.add(new_contractor)
    db.commit()
    db.refresh(new_contractor)

    return new_contractor


# ============================================================
# GET ALL CONTRACTORS
# ============================================================

@router.get(
    "/",
    response_model=list[ContractorResponse]
)
def get_contractors(
    db: Session = Depends(get_db),
):
    return (
        db.query(Contractor)
        .order_by(Contractor.id)
        .all()
    )


# ============================================================
# GET CONTRACTOR BY ID
# ============================================================

@router.get(
    "/{contractor_id}",
    response_model=ContractorResponse
)
def get_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
):
    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    return contractor


# ============================================================
# ASSIGN CONTRACTOR TO PROJECT
# ============================================================

@router.put(
    "/{contractor_id}/project/{project_id}",
    response_model=ContractorResponse
)
def assign_contractor_to_project(
    contractor_id: int,
    project_id: int,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Check contractor
    # --------------------------------------------------------

    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    # --------------------------------------------------------
    # Closed projects cannot be modified
    # --------------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified",
        )

    # --------------------------------------------------------
    # Check if contractor is already assigned
    # --------------------------------------------------------

    if contractor.project_id is not None:

        if contractor.project_id == project_id:
            raise HTTPException(
                status_code=400,
                detail="Contractor is already assigned to this project",
            )

        raise HTTPException(
            status_code=400,
            detail="Contractor is already assigned to another project",
        )

    # --------------------------------------------------------
    # Assign contractor
    # --------------------------------------------------------

    contractor.project_id = project_id

    db.commit()
    db.refresh(contractor)

    return contractor


# ============================================================
# UPDATE CONTRACTOR
# ============================================================

@router.put(
    "/{contractor_id}",
    response_model=ContractorResponse
)
def update_contractor(
    contractor_id: int,
    contractor_data: ContractorCreate,
    db: Session = Depends(get_db),
):
    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    for key, value in contractor_data.model_dump().items():
        setattr(contractor, key, value)

    db.commit()
    db.refresh(contractor)

    return contractor


# ============================================================
# DELETE CONTRACTOR
# ============================================================

@router.delete("/{contractor_id}")
def delete_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
):
    contractor = (
        db.query(Contractor)
        .filter(
            Contractor.id == contractor_id
        )
        .first()
    )

    if not contractor:
        raise HTTPException(
            status_code=404,
            detail="Contractor not found",
        )

    db.delete(contractor)
    db.commit()

    return {
        "message": "Contractor deleted successfully"
    }
