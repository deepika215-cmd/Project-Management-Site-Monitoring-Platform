from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.procurement import Procurement
from app.models.project import Project
from app.models.user import User

from app.schemas.procurement_schema import (
    ProcurementCreate,
    ProcurementResponse,
    ProcurementReportResponse,
)

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/procurement",
    tags=["Procurement"],
)


# ============================================================
# MODULE 8 - GET RESPONSIBLE PROJECT MANAGER
# ============================================================

def get_project_manager_email(
    db: Session,
    project_id: int,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return None

    if not project.manager_id:
        return None

    manager = (
        db.query(User)
        .filter(
            User.id == project.manager_id,
            User.role == "MANAGER",
        )
        .first()
    )

    if not manager:
        return None

    return manager.email


# ============================================================
# CREATE PROCUREMENT
# ============================================================

@router.post(
    "/",
    response_model=ProcurementResponse
)
def create_procurement(
    procurement: ProcurementCreate,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Verify project exists
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == procurement.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    new_procurement = Procurement(
        **procurement.model_dump()
    )

    db.add(new_procurement)
    db.commit()
    db.refresh(new_procurement)

    # --------------------------------------------------------
    # MODULE 8 - PROCUREMENT ALERT
    # Notify responsible Project Manager only
    # --------------------------------------------------------

    manager_email = get_project_manager_email(
        db=db,
        project_id=new_procurement.project_id,
    )

    if manager_email:

        message = (
            f"Procurement request #{new_procurement.id} created for "
            f"{new_procurement.quantity} units of "
            f"{new_procurement.item_name} "
            f"for Project #{new_procurement.project_id}. "
            f"Status: {new_procurement.status}."
        )

        create_notification(
            db=db,
            title="Procurement Request Created",
            message=message,
            recipient=manager_email,
        )

    return new_procurement


# ============================================================
# GET ALL PROCUREMENTS
# ============================================================

@router.get(
    "/",
    response_model=list[ProcurementResponse]
)
def get_procurements(
    db: Session = Depends(get_db),
):
    return db.query(Procurement).all()


# ============================================================
# PROCUREMENT REPORT
#
# This route must be before /{procurement_id}
# ============================================================

@router.get(
    "/report",
    response_model=ProcurementReportResponse
)
def get_procurement_report(
    db: Session = Depends(get_db),
):
    procurements = db.query(Procurement).all()

    total_requests = len(procurements)

    pending_count = 0
    approved_count = 0
    rejected_count = 0
    completed_count = 0

    total_quantity = 0
    used_quantity = 0

    for procurement in procurements:

        status = (
            procurement.status or ""
        ).strip().upper()

        if status == "PENDING":
            pending_count += 1

        elif status == "APPROVED":
            approved_count += 1

        elif status == "REJECTED":
            rejected_count += 1

        elif status in [
            "COMPLETED",
            "RECEIVED",
            "DELIVERED"
        ]:
            completed_count += 1

        quantity = procurement.quantity or 0
        used = procurement.used or 0

        total_quantity += quantity
        used_quantity += used

    remaining_quantity = (
        total_quantity - used_quantity
    )

    return ProcurementReportResponse(
        total_requests=total_requests,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        completed_count=completed_count,
        total_quantity=total_quantity,
        used_quantity=used_quantity,
        remaining_quantity=remaining_quantity,
    )


# ============================================================
# GET PROCUREMENT BY ID
# ============================================================

@router.get(
    "/{procurement_id}",
    response_model=ProcurementResponse
)
def get_procurement(
    procurement_id: int,
    db: Session = Depends(get_db),
):
    procurement = (
        db.query(Procurement)
        .filter(
            Procurement.id == procurement_id
        )
        .first()
    )

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found",
        )

    return procurement


# ============================================================
# UPDATE PROCUREMENT
# ============================================================

@router.put(
    "/{procurement_id}",
    response_model=ProcurementResponse
)
def update_procurement(
    procurement_id: int,
    procurement_data: ProcurementCreate,
    db: Session = Depends(get_db),
):
    procurement = (
        db.query(Procurement)
        .filter(
            Procurement.id == procurement_id
        )
        .first()
    )

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found",
        )

    # --------------------------------------------------------
    # Save old status before updating
    # --------------------------------------------------------

    old_status = procurement.status

    # --------------------------------------------------------
    # Update procurement
    # --------------------------------------------------------

    for key, value in procurement_data.model_dump().items():
        setattr(
            procurement,
            key,
            value
        )

    # --------------------------------------------------------
    # Verify the new project exists
    # --------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == procurement.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    db.commit()
    db.refresh(procurement)

    # --------------------------------------------------------
    # MODULE 8 - PROCUREMENT STATUS ALERT
    # Notify responsible Project Manager only
    # --------------------------------------------------------

    new_status = procurement.status

    if (
        old_status != new_status
        and new_status is not None
    ):

        status_upper = (
            new_status.strip().upper()
        )

        title_map = {
            "APPROVED": "Procurement Approved",
            "REJECTED": "Procurement Rejected",
            "COMPLETED": "Procurement Completed",
            "RECEIVED": "Procurement Received",
            "DELIVERED": "Procurement Delivered",
        }

        title = title_map.get(
            status_upper,
            "Procurement Status Updated"
        )

        message = (
            f"Procurement request #{procurement.id} "
            f"for {procurement.item_name} changed from "
            f"{old_status} to {new_status}. "
            f"Project: #{procurement.project_id}."
        )

        manager_email = get_project_manager_email(
            db=db,
            project_id=procurement.project_id,
        )

        if manager_email:

            create_notification(
                db=db,
                title=title,
                message=message,
                recipient=manager_email,
            )

    return procurement


# ============================================================
# DELETE PROCUREMENT
# ============================================================

@router.delete(
    "/{procurement_id}"
)
def delete_procurement(
    procurement_id: int,
    db: Session = Depends(get_db),
):
    procurement = (
        db.query(Procurement)
        .filter(
            Procurement.id == procurement_id
        )
        .first()
    )

    if not procurement:
        raise HTTPException(
            status_code=404,
            detail="Procurement not found",
        )

    db.delete(procurement)
    db.commit()

    return {
        "message": "Procurement deleted successfully"
    }
