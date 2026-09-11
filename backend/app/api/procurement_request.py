from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.procurement_request import ProcurementRequest
from app.models.user import User
from app.models.project import Project
from app.services.notification_service import create_notification
from app.schemas.procurement_request_schema import (
    ProcurementRequestCreate,
    ProcurementRequestResponse,
)
from app.core.permissions import role_required


router = APIRouter(
    prefix="/procurement-requests",
    tags=["Procurement Requests"],
)


# ============================================================
# CREATE PROCUREMENT REQUEST
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.post(
    "/",
    response_model=ProcurementRequestResponse,
)
def create_procurement_request(
    request: ProcurementRequestCreate,
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    new_request = ProcurementRequest(
        **request.model_dump(),
        status="Pending",
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    project = db.query(Project).filter(Project.id == new_request.project_id).first()
    if project and project.manager_id:
        manager = db.query(User).filter(
            User.id == project.manager_id,
            User.is_active == True,
        ).first()
        if manager:
            create_notification(
                db=db,
                title="Procurement Request Pending",
                message=(
                    f"Procurement request #{new_request.id} for {new_request.item_name} "
                    f"requires review for Project #{new_request.project_id}."
                ),
                recipient=manager.email,
                recipient_user_id=manager.id,
                notification_type="PROCUREMENT",
                project_id=new_request.project_id,
                related_entity_type="PROCUREMENT_REQUEST",
                related_entity_id=new_request.id,
                action_url="/procurement",
            )

    return new_request


# ============================================================
# GET ALL PROCUREMENT REQUESTS
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/",
    response_model=list[ProcurementRequestResponse],
)
def get_procurement_requests(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
        ])
    ),
    db: Session = Depends(get_db),
):
    return db.query(ProcurementRequest).all()


# ============================================================
# GET PROCUREMENT REQUEST BY ID
# Allowed: ADMIN, PROJECT_MANAGER, SITE_ENGINEER
# ============================================================

@router.get(
    "/{request_id}",
    response_model=ProcurementRequestResponse,
)
def get_procurement_request(
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
        .filter(ProcurementRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Procurement request not found",
        )

    return request


# ============================================================
# APPROVE PROCUREMENT REQUEST
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{request_id}/approve",
    response_model=ProcurementRequestResponse,
)
def approve_procurement_request(
    request_id: int,
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
        .filter(ProcurementRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Procurement request not found",
        )

    if request.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be approved",
        )

    request.status = "Approved"

    db.commit()
    db.refresh(request)

    requester = db.query(User).filter(User.id == request.requested_by, User.is_active == True).first()
    if requester:
        create_notification(
            db=db,
            title="Procurement Request Approved",
            message=f"Your procurement request #{request.id} for {request.item_name} was approved.",
            recipient=requester.email,
            recipient_user_id=requester.id,
            notification_type="PROCUREMENT",
            project_id=request.project_id,
            related_entity_type="PROCUREMENT_REQUEST",
            related_entity_id=request.id,
            action_url="/procurement",
        )

    return request


# ============================================================
# REJECT PROCUREMENT REQUEST
# Allowed: ADMIN, PROJECT_MANAGER
# ============================================================

@router.put(
    "/{request_id}/reject",
    response_model=ProcurementRequestResponse,
)
def reject_procurement_request(
    request_id: int,
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
        .filter(ProcurementRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Procurement request not found",
        )

    if request.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be rejected",
        )

    request.status = "Rejected"

    db.commit()
    db.refresh(request)

    requester = db.query(User).filter(User.id == request.requested_by, User.is_active == True).first()
    if requester:
        create_notification(
            db=db,
            title="Procurement Request Rejected",
            message=f"Your procurement request #{request.id} for {request.item_name} was rejected.",
            recipient=requester.email,
            recipient_user_id=requester.id,
            notification_type="PROCUREMENT",
            project_id=request.project_id,
            related_entity_type="PROCUREMENT_REQUEST",
            related_entity_id=request.id,
            action_url="/procurement",
        )

    return request