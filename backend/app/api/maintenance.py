from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.maintenance import Maintenance
from app.models.machinery import Machinery
from app.models.notification import Notification

from app.schemas.maintenance_schema import (
    MaintenanceCreate,
    MaintenanceResponse,
    MaintenanceStatusUpdate,
    MaintenanceCompletion,
)


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


# ============================================================
# CREATE MAINTENANCE
# ============================================================

@router.post("/", response_model=MaintenanceResponse)
def create_maintenance(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    machinery = (
        db.query(Machinery)
        .filter(Machinery.id == maintenance.machinery_id)
        .first()
    )

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    new_maintenance = Maintenance(
        machinery_id=maintenance.machinery_id,
        maintenance_type=maintenance.maintenance_type,
        description=maintenance.description,
        scheduled_date=maintenance.scheduled_date,
        completion_date=maintenance.completion_date,
        status=maintenance.status,
        cost=maintenance.cost,
        technician=maintenance.technician
    )

    db.add(new_maintenance)
    db.commit()
    db.refresh(new_maintenance)

    return new_maintenance


# ============================================================
# GET ALL MAINTENANCE
# ============================================================

@router.get("/", response_model=list[MaintenanceResponse])
def get_maintenance(
    db: Session = Depends(get_db)
):
    return (
        db.query(Maintenance)
        .order_by(Maintenance.id.desc())
        .all()
    )


# ============================================================
# GET UPCOMING MAINTENANCE
# ============================================================

@router.get(
    "/upcoming",
    response_model=list[MaintenanceResponse]
)
def get_upcoming_maintenance(
    db: Session = Depends(get_db)
):
    return (
        db.query(Maintenance)
        .filter(
            Maintenance.scheduled_date >= date.today(),
            Maintenance.status != "Completed"
        )
        .order_by(Maintenance.scheduled_date)
        .all()
    )


# ============================================================
# AUTOMATIC MAINTENANCE NOTIFICATIONS
#
# Creates notifications for maintenance scheduled within
# the next 7 days.
#
# Notifications are created for:
# ADMIN
# MANAGER
#
# Duplicate notifications are prevented.
# ============================================================

@router.get("/notifications")
def get_maintenance_notifications(
    db: Session = Depends(get_db)
):
    today = date.today()
    notification_end_date = today + timedelta(days=7)

    upcoming_maintenance = (
        db.query(Maintenance)
        .filter(
            Maintenance.scheduled_date >= today,
            Maintenance.scheduled_date <= notification_end_date,
            Maintenance.status != "Completed"
        )
        .order_by(Maintenance.scheduled_date)
        .all()
    )

    created_notifications = []

    for maintenance in upcoming_maintenance:

        machinery = (
            db.query(Machinery)
            .filter(Machinery.id == maintenance.machinery_id)
            .first()
        )

        machinery_name = (
            machinery.name
            if machinery
            else f"Machinery {maintenance.machinery_id}"
        )

        title = "Maintenance Due Soon"

        message = (
            f"Maintenance for {machinery_name} is scheduled on "
            f"{maintenance.scheduled_date}. "
            f"Maintenance type: {maintenance.maintenance_type}."
        )

        for recipient in ["ADMIN", "MANAGER"]:

            existing_notification = (
                db.query(Notification)
                .filter(
                    Notification.title == title,
                    Notification.message == message,
                    Notification.recipient == recipient
                )
                .first()
            )

            if existing_notification:
                continue

            notification = Notification(
                title=title,
                message=message,
                recipient=recipient,
                status="Unread"
            )

            db.add(notification)
            db.flush()

            created_notifications.append(notification)

    db.commit()

    return {
        "message": "Maintenance notifications processed successfully",
        "notifications_created": len(created_notifications),
        "notifications": [
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "recipient": notification.recipient,
                "status": notification.status
            }
            for notification in created_notifications
        ]
    }


# ============================================================
# GET MAINTENANCE BY ID
# ============================================================

@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def get_maintenance_by_id(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = (
        db.query(Maintenance)
        .filter(Maintenance.id == maintenance_id)
        .first()
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    return maintenance


# ============================================================
# UPDATE MAINTENANCE
# ============================================================

@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceResponse
)
def update_maintenance(
    maintenance_id: int,
    maintenance_data: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    maintenance = (
        db.query(Maintenance)
        .filter(Maintenance.id == maintenance_id)
        .first()
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    machinery = (
        db.query(Machinery)
        .filter(Machinery.id == maintenance_data.machinery_id)
        .first()
    )

    if not machinery:
        raise HTTPException(
            status_code=404,
            detail="Machinery not found"
        )

    maintenance.machinery_id = maintenance_data.machinery_id
    maintenance.maintenance_type = maintenance_data.maintenance_type
    maintenance.description = maintenance_data.description
    maintenance.scheduled_date = maintenance_data.scheduled_date
    maintenance.completion_date = maintenance_data.completion_date
    maintenance.status = maintenance_data.status
    maintenance.cost = maintenance_data.cost
    maintenance.technician = maintenance_data.technician

    db.commit()
    db.refresh(maintenance)

    return maintenance


# ============================================================
# UPDATE MAINTENANCE STATUS
# ============================================================

@router.put(
    "/{maintenance_id}/status",
    response_model=MaintenanceResponse
)
def update_maintenance_status(
    maintenance_id: int,
    status_data: MaintenanceStatusUpdate,
    db: Session = Depends(get_db)
):
    maintenance = (
        db.query(Maintenance)
        .filter(Maintenance.id == maintenance_id)
        .first()
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    maintenance.status = status_data.status

    db.commit()
    db.refresh(maintenance)

    return maintenance


# ============================================================
# COMPLETE MAINTENANCE
# ============================================================

@router.put(
    "/{maintenance_id}/complete",
    response_model=MaintenanceResponse
)
def complete_maintenance(
    maintenance_id: int,
    completion_data: MaintenanceCompletion,
    db: Session = Depends(get_db)
):
    maintenance = (
        db.query(Maintenance)
        .filter(Maintenance.id == maintenance_id)
        .first()
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    maintenance.completion_date = completion_data.completion_date
    maintenance.status = "Completed"

    db.commit()
    db.refresh(maintenance)

    return maintenance


# ============================================================
# DELETE MAINTENANCE
# ============================================================

@router.delete("/{maintenance_id}")
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = (
        db.query(Maintenance)
        .filter(Maintenance.id == maintenance_id)
        .first()
    )

    if not maintenance:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    db.delete(maintenance)
    db.commit()

    return {
        "message": "Maintenance record deleted successfully"
    }