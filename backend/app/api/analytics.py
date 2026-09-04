from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.project import Project
from app.models.worker import Worker
from app.models.attendance import Attendance
from app.models.resource import Resource
from app.models.inventory import Inventory
from app.models.procurement import Procurement
from app.models.project_milestone import ProjectMilestone
from app.models.daily_progress import DailyProgress
from app.models.report import Report
from app.models.material import Material
from app.models.stock_movement import StockMovement

from app.schemas.analytics_schema import (
    AnalyticsResponse,
    ResourceUtilization
)

from app.schemas.project_progress import ProjectProgress
from app.schemas.inventory_analytics import InventoryAnalytics
from app.schemas.procurement_analytics import ProcurementAnalytics
from app.schemas.worker_analytics import WorkerAnalytics
from app.schemas.report_analytics import ReportAnalytics
from app.schemas.project_analytics import ProjectAnalytics


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ============================================================
# GENERAL ANALYTICS
# ============================================================

@router.get(
    "/",
    response_model=AnalyticsResponse
)
def get_analytics(
    db: Session = Depends(get_db)
):
    """
    Returns overall project, workforce, resource,
    inventory and procurement analytics.
    """

    total_projects = db.query(Project).count()

    # Project lifecycle:
    # Planning -> In Progress -> On Hold -> Completed -> Closed

    active_projects = db.query(Project).filter(
        Project.status == "In Progress"
    ).count()

    completed_projects = db.query(Project).filter(
        Project.status.in_(["Completed", "Closed"])
    ).count()

    pending_projects = db.query(Project).filter(
        Project.status.in_(["Planning", "On Hold"])
    ).count()

    total_workers = db.query(Worker).count()

    present_workers = db.query(Attendance).filter(
        Attendance.status == "Present"
    ).count()

    absent_workers = db.query(Attendance).filter(
        Attendance.status == "Absent"
    ).count()

    total_resources = db.query(Resource).count()

    total_inventory = db.query(Inventory).count()

    total_procurements = db.query(Procurement).count()

    return {
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "completed": completed_projects,
            "pending": pending_projects
        },
        "workers": {
            "total": total_workers,
            "present": present_workers,
            "absent": absent_workers
        },
        "resources": {
            "total": total_resources
        },
        "inventory": {
            "total": total_inventory
        },
        "procurements": {
            "total": total_procurements
        }
    }


# ============================================================
# PROJECT PROGRESS
# ============================================================

@router.get(
    "/project-progress",
    response_model=list[ProjectProgress]
)
def project_progress(
    db: Session = Depends(get_db)
):
    """
    Returns actual project progress.

    Progress is calculated from Daily Progress reports.

    For each work category, only the latest progress
    percentage is used.

    Overall project progress is the average of the
    latest progress percentage of each work category.

    If no Daily Progress exists, milestone progress is
    used as a fallback.

    Milestone information is also returned.
    """

    projects = db.query(Project).all()

    result = []

    for project in projects:

        # ----------------------------------------------------
        # Get milestones for this project
        # ----------------------------------------------------

        milestones = db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project.id
        ).all()

        total_milestones = len(milestones)

        completed_milestones = len([
            milestone
            for milestone in milestones
            if milestone.status == "Completed"
        ])

        # ----------------------------------------------------
        # Get daily progress records
        # ----------------------------------------------------

        daily_progress_records = (
            db.query(DailyProgress)
            .filter(
                DailyProgress.project_id == project.id
            )
            .order_by(
                DailyProgress.report_date.asc(),
                DailyProgress.id.asc()
            )
            .all()
        )

        # ----------------------------------------------------
        # Calculate actual construction progress
        # ----------------------------------------------------

        progress = 0.0

        if daily_progress_records:

            latest_progress_by_category = {}

            for record in daily_progress_records:

                category = record.work_category

                if record.completion_percentage is not None:

                    latest_progress_by_category[category] = (
                        record.completion_percentage
                    )

            if latest_progress_by_category:

                progress = round(
                    sum(
                        latest_progress_by_category.values()
                    )
                    / len(latest_progress_by_category),
                    2
                )

        # ----------------------------------------------------
        # If no Daily Progress exists, use milestone progress
        # as a fallback.
        # ----------------------------------------------------

        elif total_milestones > 0:

            progress = round(
                (
                    completed_milestones
                    / total_milestones
                ) * 100,
                2
            )

        result.append({
            "project_id": project.id,
            "project_name": project.project_name,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "progress": progress
        })

    return result


# ============================================================
# RESOURCE UTILIZATION
# ============================================================

@router.get(
    "/resource-utilization",
    response_model=list[ResourceUtilization]
)
def resource_utilization(
    db: Session = Depends(get_db)
):
    """
    Returns resource allocation and utilization.
    """

    resources = db.query(Resource).all()

    result = []

    for resource in resources:

        total_quantity = resource.quantity or 0
        allocated = resource.allocated_quantity or 0

        available = total_quantity - allocated

        utilization = 0.0

        if total_quantity > 0:

            utilization = round(
                (allocated / total_quantity) * 100,
                2
            )

        result.append({
            "resource_id": resource.id,
            "resource_name": resource.name,
            "available": available,
            "allocated": allocated,
            "utilization": utilization
        })

    return result


# ============================================================
# INVENTORY STATUS
# ============================================================

@router.get(
    "/inventory-status",
    response_model=list[InventoryAnalytics]
)
def inventory_status(
    db: Session = Depends(get_db)
):
    """
    Returns inventory quantity, consumed quantity
    and remaining quantity.

    The Inventory model does not contain a 'used' column.
    Therefore, consumed quantity is calculated from
    StockMovement records.
    """

    inventory_items = db.query(Inventory).all()

    result = []

    for item in inventory_items:

        quantity = item.quantity or 0

        # ----------------------------------------------------
        # Find matching Material
        # ----------------------------------------------------

        material = db.query(Material).filter(
            Material.name == item.item_name
        ).first()

        used = 0

        # ----------------------------------------------------
        # Calculate consumed quantity from StockMovement
        # ----------------------------------------------------

        if material:

            consumed_movements = db.query(
                StockMovement
            ).filter(
                StockMovement.material_id == material.id,
                StockMovement.movement_type == "CONSUMED"
            ).all()

            used = sum(
                movement.quantity or 0
                for movement in consumed_movements
            )

        # ----------------------------------------------------
        # Calculate remaining inventory
        # ----------------------------------------------------

        remaining = max(
            quantity - used,
            0
        )

        result.append({
            "inventory_id": item.id,
            "item_name": item.item_name,
            "quantity": quantity,
            "used": used,
            "remaining": remaining
        })

    return result


# ============================================================
# PROCUREMENT STATUS
# ============================================================

@router.get(
    "/procurement-status",
    response_model=list[ProcurementAnalytics]
)
def procurement_status(
    db: Session = Depends(get_db)
):
    """
    Returns procurement ordered, received and pending quantities.
    """

    procurements = db.query(Procurement).all()

    result = []

    for procurement in procurements:

        ordered = procurement.quantity or 0

        if procurement.status == "Received":
            received = ordered
        else:
            received = 0

        pending = ordered - received

        result.append({
            "procurement_id": procurement.id,
            "item_name": procurement.item_name,
            "supplier": procurement.supplier,
            "ordered": ordered,
            "received": received,
            "pending": pending
        })

    return result


# ============================================================
# WORKER ATTENDANCE
# ============================================================

@router.get(
    "/worker-attendance",
    response_model=list[WorkerAnalytics]
)
def worker_attendance(
    db: Session = Depends(get_db)
):
    """
    Returns attendance analytics for every worker.
    """

    workers = db.query(Worker).all()

    result = []

    for worker in workers:

        attendance = db.query(Attendance).filter(
            Attendance.worker_id == worker.id
        ).all()

        present = len([
            record
            for record in attendance
            if record.status == "Present"
        ])

        absent = len([
            record
            for record in attendance
            if record.status == "Absent"
        ])

        total = present + absent

        percentage = 0.0

        if total > 0:

            percentage = round(
                (present / total) * 100,
                2
            )

        result.append({
            "worker_id": worker.id,
            "worker_name": worker.name,
            "present_days": present,
            "absent_days": absent,
            "attendance_percentage": percentage
        })

    return result


# ============================================================
# PROJECT SUMMARY
# ============================================================

@router.get(
    "/project-summary",
    response_model=list[ProjectAnalytics]
)
def project_summary(
    db: Session = Depends(get_db)
):
    """
    Returns project status and actual construction progress.

    Progress is calculated from the latest Daily Progress
    record for each work category.

    If no Daily Progress exists, milestone progress is
    used as a fallback.
    """

    projects = db.query(Project).all()

    result = []

    for project in projects:

        # ----------------------------------------------------
        # Get daily progress
        # ----------------------------------------------------

        daily_progress_records = (
            db.query(DailyProgress)
            .filter(
                DailyProgress.project_id == project.id
            )
            .order_by(
                DailyProgress.report_date.asc(),
                DailyProgress.id.asc()
            )
            .all()
        )

        # ----------------------------------------------------
        # Calculate actual construction progress
        # ----------------------------------------------------

        progress = 0.0

        if daily_progress_records:

            latest_progress_by_category = {}

            for record in daily_progress_records:

                category = record.work_category

                if record.completion_percentage is not None:

                    latest_progress_by_category[category] = (
                        record.completion_percentage
                    )

            if latest_progress_by_category:

                progress = round(
                    sum(
                        latest_progress_by_category.values()
                    )
                    / len(latest_progress_by_category),
                    2
                )

        # ----------------------------------------------------
        # Fallback to milestone progress
        # ----------------------------------------------------

        else:

            milestones = db.query(ProjectMilestone).filter(
                ProjectMilestone.project_id == project.id
            ).all()

            total = len(milestones)

            completed = len([
                milestone
                for milestone in milestones
                if milestone.status == "Completed"
            ])

            if total > 0:

                progress = round(
                    (completed / total) * 100,
                    2
                )

        result.append({
            "project_id": project.id,
            "project_name": project.project_name,
            "status": project.status,
            "progress": progress
        })

    return result


# ============================================================
# REPORT SUMMARY
# ============================================================

@router.get(
    "/report-summary",
    response_model=list[ReportAnalytics]
)
def report_summary(
    db: Session = Depends(get_db)
):
    """
    Returns report information for analytics.
    """

    reports = db.query(Report).all()

    result = []

    for report in reports:

        result.append({
            "report_id": report.id,
            "title": report.title,
            "report_type": report.report_type,
            "status": report.status
        })

    return result