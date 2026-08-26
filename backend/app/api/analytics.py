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
from app.models.report import Report

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


@router.get("/", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):

    total_projects = db.query(Project).count()

    active_projects = db.query(Project).filter(
        Project.status == "Active"
    ).count()

    completed_projects = db.query(Project).filter(
        Project.status == "Completed"
    ).count()

    pending_projects = db.query(Project).filter(
        Project.status == "Pending"
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


@router.get(
    "/project-progress",
    response_model=list[ProjectProgress]
)
def project_progress(db: Session = Depends(get_db)):

    projects = db.query(Project).all()

    result = []

    for project in projects:

        milestones = db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project.id
        ).all()

        total = len(milestones)

        completed = len([
            milestone
            for milestone in milestones
            if milestone.status == "Completed"
        ])

        progress = 0

        if total > 0:
            progress = round((completed / total) * 100, 2)

        result.append({
            "project_id": project.id,
            "project_name": project.project_name,
            "total_milestones": total,
            "completed_milestones": completed,
            "progress": progress
        })

    return result


@router.get(
    "/resource-utilization",
    response_model=list[ResourceUtilization]
)
def resource_utilization(db: Session = Depends(get_db)):

    resources = db.query(Resource).all()

    result = []

    for resource in resources:

        total_quantity = resource.quantity
        allocated = resource.allocated_quantity

        available = total_quantity - allocated

        utilization = 0

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


@router.get(
    "/inventory-status",
    response_model=list[InventoryAnalytics]
)
def inventory_status(db: Session = Depends(get_db)):

    inventory = db.query(Inventory).all()

    result = []

    for item in inventory:

        remaining = item.quantity - item.used

        result.append({
            "inventory_id": item.id,
            "item_name": item.material_name,
            "quantity": item.quantity,
            "used": item.used,
            "remaining": remaining
        })

    return result


@router.get(
    "/procurement-status",
    response_model=list[ProcurementAnalytics]
)
def procurement_status(db: Session = Depends(get_db)):

    procurements = db.query(Procurement).all()

    result = []

    for procurement in procurements:

        ordered = procurement.quantity

        received = ordered if procurement.status == "Received" else 0

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


@router.get(
    "/worker-attendance",
    response_model=list[WorkerAnalytics]
)
def worker_attendance(db: Session = Depends(get_db)):

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

        percentage = 0

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


@router.get(
    "/project-summary",
    response_model=list[ProjectAnalytics]
)
def project_summary(db: Session = Depends(get_db)):

    projects = db.query(Project).all()

    result = []

    for project in projects:

        milestones = db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project.id
        ).all()

        total = len(milestones)

        completed = len([
            milestone
            for milestone in milestones
            if milestone.status == "Completed"
        ])

        progress = 0

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


@router.get(
    "/report-summary",
    response_model=list[ReportAnalytics]
)
def report_summary(db: Session = Depends(get_db)):

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