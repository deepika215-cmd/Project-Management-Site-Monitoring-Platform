from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.resource import Resource
from app.models.project import Project
from app.models.resource_utilization import ResourceUtilization


router = APIRouter(
    prefix="/resource-utilization",
    tags=["Resource Utilization"]
)


# =========================================================
# Create Resource Utilization Record
# =========================================================

@router.post("/")
def create_resource_utilization(
    resource_id: int,
    project_id: int,
    usage_date: date,
    hours_used: float,
    status: str = "Used",
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

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if hours_used < 0:
        raise HTTPException(
            status_code=400,
            detail="Hours used cannot be negative"
        )

    utilization = ResourceUtilization(
        resource_id=resource_id,
        project_id=project_id,
        usage_date=usage_date,
        hours_used=hours_used,
        status=status
    )

    db.add(utilization)
    db.commit()
    db.refresh(utilization)

    return utilization


# =========================================================
# Get All Utilization Records
# =========================================================

@router.get("/")
def get_resource_utilization(
    db: Session = Depends(get_db)
):
    return db.query(ResourceUtilization).all()


# =========================================================
# Get Detailed Utilization History
# =========================================================

@router.get("/{resource_id}")
def get_resource_utilization_by_resource(
    resource_id: int,
    start_date: date,
    end_date: date,
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

    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # -----------------------------------------------------
    # Get utilization records for the requested period
    # -----------------------------------------------------

    records = db.query(ResourceUtilization).filter(
        ResourceUtilization.resource_id == resource_id,
        ResourceUtilization.usage_date >= start_date,
        ResourceUtilization.usage_date <= end_date
    ).order_by(
        ResourceUtilization.usage_date
    ).all()

    # -----------------------------------------------------
    # Calculate total days
    # -----------------------------------------------------

    total_days = (
        end_date - start_date
    ).days + 1

    # -----------------------------------------------------
    # Calculate used days
    # -----------------------------------------------------

    used_dates = set(
        record.usage_date
        for record in records
        if record.hours_used > 0
    )

    used_days = len(used_dates)

    # -----------------------------------------------------
    # Calculate idle days
    # -----------------------------------------------------

    idle_days = total_days - used_days

    # -----------------------------------------------------
    # Calculate total hours
    # -----------------------------------------------------

    total_hours = sum(
        record.hours_used
        for record in records
    )

    # -----------------------------------------------------
    # Calculate utilization percentage
    # -----------------------------------------------------

    utilization_percentage = round(
        (used_days / total_days) * 100,
        2
    ) if total_days > 0 else 0.0

    # -----------------------------------------------------
    # Calculate allocation frequency
    #
    # Each utilization record represents one usage entry.
    # -----------------------------------------------------

    allocation_frequency = len(records)

    # -----------------------------------------------------
    # Find unique projects used
    # -----------------------------------------------------

    projects_used = sorted(
        set(
            record.project_id
            for record in records
        )
    )

    # -----------------------------------------------------
    # Return detailed utilization history
    # -----------------------------------------------------

    return {
        "resource_id": resource.id,
        "resource_name": resource.name,
        "period_start": start_date,
        "period_end": end_date,
        "total_days": total_days,
        "used_days": used_days,
        "idle_days": idle_days,
        "total_hours_used": total_hours,
        "allocation_frequency": allocation_frequency,
        "projects_used": projects_used,
        "utilization_percentage": utilization_percentage,
        "records": records
    }