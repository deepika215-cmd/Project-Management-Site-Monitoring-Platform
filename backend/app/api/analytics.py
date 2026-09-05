from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.project import Project
from app.models.worker import Worker
from app.models.worker_assignment import WorkerAssignment
from app.models.attendance import Attendance
from app.models.resource import Resource
from app.models.inventory import Inventory
from app.models.procurement import Procurement
from app.models.project_milestone import ProjectMilestone
from app.models.daily_progress import DailyProgress
from app.models.report import Report
from app.models.material import Material
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.models.site_activity_log import SiteActivityLog
from app.models.payroll import Payroll
from app.models.maintenance import Maintenance
from app.models.machinery import Machinery

from app.core.permissions import role_required

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
from app.schemas.manager_dashboard_schema import (
    ManagerDashboardResponse
)
from app.schemas.admin_dashboard_schema import (
    AdminDashboardResponse
)
from app.schemas.activity_monitoring_schema import (
    ActivityMonitoringResponse
)
from app.schemas.project_dashboard_schema import (
    ProjectDashboardResponse
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_project_progress(
    db: Session,
    project_id: int
) -> float:
    """
    Calculate project progress.

    Priority:
    1. Latest DailyProgress percentage by work category
    2. Completed milestones / total milestones
    3. 0 if no progress data exists
    """

    milestones = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.project_id == project_id
        )
        .all()
    )

    total_milestones = len(milestones)

    completed_milestones = sum(
        1
        for milestone in milestones
        if str(
            getattr(
                milestone,
                "status",
                ""
            ) or ""
        ).upper() == "COMPLETED"
    )

    daily_progress_rows = (
        db.query(DailyProgress)
        .filter(
            DailyProgress.project_id == project_id
        )
        .all()
    )

    if daily_progress_rows:

        latest_by_category = {}

        for row in daily_progress_rows:

            category = getattr(
                row,
                "work_category",
                None
            )

            if category is None:
                category = getattr(
                    row,
                    "work_activity",
                    None
                )

            if category is None:
                category = "GENERAL"

            existing = latest_by_category.get(
                category
            )

            if existing is None:
                latest_by_category[category] = row
                continue

            row_date = getattr(
                row,
                "date",
                None
            )

            existing_date = getattr(
                existing,
                "date",
                None
            )

            if row_date is not None:

                if (
                    existing_date is None
                    or row_date > existing_date
                ):
                    latest_by_category[category] = row

        percentages = []

        for row in latest_by_category.values():

            percentage = getattr(
                row,
                "completion_percentage",
                None
            )

            if percentage is not None:
                percentages.append(
                    float(percentage)
                )

        if percentages:

            return round(
                sum(percentages)
                / len(percentages),
                2
            )

    # --------------------------------------------------------
    # MILESTONE FALLBACK
    # --------------------------------------------------------

    if total_milestones > 0:

        return round(
            (
                completed_milestones
                / total_milestones
            ) * 100,
            2
        )

    return 0.0


# ============================================================
# OVERALL ANALYTICS
# ============================================================

@router.get(
    "/",
    response_model=AnalyticsResponse
)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    total_projects = db.query(Project).count()

    active_projects = (
        db.query(Project)
        .filter(
            Project.status == "Active"
        )
        .count()
    )

    completed_projects = (
        db.query(Project)
        .filter(
            Project.status == "Closed"
        )
        .count()
    )

    pending_projects = (
        total_projects
        - active_projects
        - completed_projects
    )

    total_workers = db.query(Worker).count()

    today = date.today().isoformat()

    present_workers = (
        db.query(Attendance)
        .filter(
            Attendance.date == today,
            Attendance.status == "Present"
        )
        .count()
    )

    absent_workers = (
        db.query(Attendance)
        .filter(
            Attendance.date == today,
            Attendance.status == "Absent"
        )
        .count()
    )

    total_resources = (
        db.query(Resource).count()
    )

    total_inventory = (
        db.query(Inventory).count()
    )

    total_procurements = (
        db.query(Procurement).count()
    )

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
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    projects = db.query(Project).all()

    result = []

    for project in projects:

        total_milestones = (
            db.query(ProjectMilestone)
            .filter(
                ProjectMilestone.project_id
                == project.id
            )
            .count()
        )

        completed_milestones = (
            db.query(ProjectMilestone)
            .filter(
                ProjectMilestone.project_id
                == project.id,
                ProjectMilestone.status
                == "COMPLETED"
            )
            .count()
        )

        progress = calculate_project_progress(
            db,
            project.id
        )

        result.append(
            {
                "project_id": project.id,
                "project_name": project.project_name,
                "total_milestones":
                    total_milestones,
                "completed_milestones":
                    completed_milestones,
                "progress": progress
            }
        )

    return result


# ============================================================
# RESOURCE UTILIZATION
# ============================================================

@router.get(
    "/resource-utilization",
    response_model=list[ResourceUtilization]
)
def resource_utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    resources = db.query(Resource).all()

    result = []

    for resource in resources:

        total_quantity = (
            resource.quantity or 0
        )

        allocated_quantity = (
            resource.allocated_quantity or 0
        )

        available_quantity = (
            total_quantity
            - allocated_quantity
        )

        utilization = 0.0

        if total_quantity > 0:

            utilization = round(
                (
                    allocated_quantity
                    / total_quantity
                ) * 100,
                2
            )

        result.append(
            {
                "resource_id": resource.id,
                "resource_name": resource.name,
                "available":
                    available_quantity,
                "allocated":
                    allocated_quantity,
                "utilization":
                    utilization
            }
        )

    return result


# ============================================================
# INVENTORY STATUS
# ============================================================

@router.get(
    "/inventory-status",
    response_model=list[InventoryAnalytics]
)
def inventory_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    inventory_items = (
        db.query(Inventory).all()
    )

    result = []

    for item in inventory_items:

        quantity = item.quantity or 0

        used = 0

        movements = (
            db.query(StockMovement)
            .filter(
                StockMovement.project_id
                == item.project_id,
                StockMovement.material_id
                == getattr(
                    item,
                    "material_id",
                    None
                )
            )
            .all()
        )

        for movement in movements:

            movement_type = str(
                movement.movement_type or ""
            ).upper()

            if movement_type in [
                "OUT",
                "ISSUE",
                "USED",
                "CONSUMED"
            ]:
                used += (
                    movement.quantity or 0
                )

        remaining = max(
            quantity - used,
            0
        )

        result.append(
            {
                "inventory_id": item.id,
                "item_name": item.item_name,
                "quantity": quantity,
                "used": used,
                "remaining": remaining
            }
        )

    return result


# ============================================================
# PROCUREMENT STATUS
# ============================================================

@router.get(
    "/procurement-status",
    response_model=list[ProcurementAnalytics]
)
def procurement_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    procurements = (
        db.query(Procurement).all()
    )

    result = []

    for procurement in procurements:

        ordered = (
            procurement.quantity or 0
        )

        received = (
            procurement.used or 0
        )

        pending = max(
            ordered - received,
            0
        )

        result.append(
            {
                "procurement_id":
                    procurement.id,
                "item_name":
                    procurement.item_name,
                "supplier":
                    procurement.supplier,
                "ordered":
                    ordered,
                "received":
                    received,
                "pending":
                    pending
            }
        )

    return result


# ============================================================
# WORKER ATTENDANCE
# ============================================================

@router.get(
    "/worker-attendance",
    response_model=list[WorkerAnalytics]
)
def worker_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    workers = db.query(Worker).all()

    result = []

    for worker in workers:

        attendance_records = (
            db.query(Attendance)
            .filter(
                Attendance.worker_id
                == worker.id
            )
            .all()
        )

        present_days = sum(
            1
            for attendance
            in attendance_records
            if str(
                attendance.status or ""
            ).upper() == "PRESENT"
        )

        absent_days = sum(
            1
            for attendance
            in attendance_records
            if str(
                attendance.status or ""
            ).upper() == "ABSENT"
        )

        total_days = (
            present_days
            + absent_days
        )

        attendance_percentage = 0.0

        if total_days > 0:

            attendance_percentage = round(
                (
                    present_days
                    / total_days
                ) * 100,
                2
            )

        result.append(
            {
                "worker_id":
                    worker.id,
                "worker_name":
                    worker.name,
                "present_days":
                    present_days,
                "absent_days":
                    absent_days,
                "attendance_percentage":
                    attendance_percentage
            }
        )

    return result


# ============================================================
# PROJECT SUMMARY
# ============================================================

@router.get(
    "/project-summary",
    response_model=list[ProjectAnalytics]
)
def project_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    projects = db.query(Project).all()

    result = []

    for project in projects:

        progress = calculate_project_progress(
            db,
            project.id
        )

        result.append(
            {
                "project_id":
                    project.id,
                "project_name":
                    project.project_name,
                "status":
                    project.status,
                "progress":
                    progress
            }
        )

    return result


# ============================================================
# REPORT SUMMARY
# ============================================================

@router.get(
    "/report-summary",
    response_model=list[ReportAnalytics]
)
def report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    reports = db.query(Report).all()

    result = []

    for report in reports:

        result.append(
            {
                "report_id":
                    report.id,
                "title":
                    report.title,
                "report_type":
                    report.report_type,
                "status":
                    report.status
            }
        )

    return result


# ============================================================
# MANAGER DASHBOARD
# ============================================================

@router.get(
    "/manager-dashboard",
    response_model=ManagerDashboardResponse
)
def manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["MANAGER"])
    )
):

    # ========================================================
    # MANAGER PROJECT FILTER
    # ========================================================

    projects = (
        db.query(Project)
        .filter(
            Project.manager_id
            == current_user.id
        )
        .all()
    )

    project_ids = [
        project.id
        for project in projects
    ]

    # ========================================================
    # NO PROJECTS ASSIGNED
    # ========================================================

    if not project_ids:

        return {
            "project_progress": [],

            "budget": {
                "total_budget": 0,
                "total_actual_cost": 0,
                "remaining_budget": 0,
                "utilization_percentage": 0
            },

            "workforce": {
                "total_workers": 0,
                "active_allocations": 0,
                "present": 0,
                "absent": 0
            },

            "resources": {
                "total_quantity": 0,
                "allocated_quantity": 0,
                "available_quantity": 0,
                "utilization": 0
            },

            "procurement": {
                "total_procurements": 0,
                "pending_procurements": 0,
                "completed_procurements": 0
            }
        }

    # ========================================================
    # PROJECT PROGRESS
    # ========================================================

    project_progress = []

    for project in projects:

        progress = calculate_project_progress(
            db,
            project.id
        )

        project_progress.append(
            {
                "project_id":
                    project.id,
                "project_name":
                    project.project_name,
                "progress":
                    progress
            }
        )

    # ========================================================
    # BUDGET UTILIZATION
    # ========================================================

    total_budget = 0.0
    total_labour_cost = 0.0
    total_material_cost = 0.0
    total_procurement_cost = 0.0
    total_maintenance_cost = 0.0

    for project in projects:

        project_budget = float(
            getattr(
                project,
                "budget",
                0
            ) or 0
        )

        total_budget += project_budget

        # ----------------------------------------------------
        # LABOUR COST
        # ----------------------------------------------------

        payroll_records = (
            db.query(Payroll)
            .filter(
                Payroll.project_id
                == project.id
            )
            .all()
        )

        total_labour_cost += sum(
            float(
                payroll.estimated_pay or 0
            )
            for payroll
            in payroll_records
        )

        # ----------------------------------------------------
        # MATERIAL COST
        # ----------------------------------------------------

        total_material_cost += 0.0

        # ----------------------------------------------------
        # PROCUREMENT COST
        # ----------------------------------------------------

        total_procurement_cost += 0.0

        # ----------------------------------------------------
        # MAINTENANCE COST
        # ----------------------------------------------------

        maintenance_records = (
            db.query(Maintenance)
            .join(
                Machinery,
                Maintenance.machinery_id
                == Machinery.id
            )
            .filter(
                Machinery.project_id
                == project.id
            )
            .all()
        )

        total_maintenance_cost += sum(
            float(
                maintenance.cost or 0
            )
            for maintenance
            in maintenance_records
        )

    total_actual_cost = round(
        total_labour_cost
        + total_material_cost
        + total_procurement_cost
        + total_maintenance_cost,
        2
    )

    remaining_budget = round(
        total_budget
        - total_actual_cost,
        2
    )

    utilization_percentage = 0.0

    if total_budget > 0:

        utilization_percentage = round(
            (
                total_actual_cost
                / total_budget
            ) * 100,
            2
        )

    # ========================================================
    # WORKFORCE
    # ========================================================

    worker_assignments = (
        db.query(WorkerAssignment)
        .filter(
            WorkerAssignment.project_id.in_(
                project_ids
            )
        )
        .all()
    )

    worker_ids = {
        assignment.worker_id
        for assignment
        in worker_assignments
    }

    total_workers = len(worker_ids)

    active_allocations = (
        db.query(WorkerAssignment)
        .filter(
            WorkerAssignment.project_id.in_(
                project_ids
            ),
            WorkerAssignment.assignment_status
            == "ACTIVE"
        )
        .count()
    )

    # ========================================================
    # TODAY'S ATTENDANCE
    # ========================================================

    today = date.today().isoformat()

    present = (
        db.query(Attendance)
        .filter(
            Attendance.project_id.in_(
                project_ids
            ),
            Attendance.date == today,
            Attendance.status == "Present"
        )
        .count()
    )

    absent = (
        db.query(Attendance)
        .filter(
            Attendance.project_id.in_(
                project_ids
            ),
            Attendance.date == today,
            Attendance.status == "Absent"
        )
        .count()
    )

    # ========================================================
    # RESOURCE UTILIZATION
    # ========================================================

    resources = (
        db.query(Resource)
        .filter(
            Resource.project_id.in_(
                project_ids
            )
        )
        .all()
    )

    total_quantity = sum(
        resource.quantity or 0
        for resource in resources
    )

    allocated_quantity = sum(
        resource.allocated_quantity or 0
        for resource in resources
    )

    available_quantity = (
        total_quantity
        - allocated_quantity
    )

    utilization = 0.0

    if total_quantity > 0:

        utilization = round(
            (
                allocated_quantity
                / total_quantity
            ) * 100,
            2
        )

    # ========================================================
    # PROCUREMENT OVERVIEW
    # ========================================================

    procurements = (
        db.query(Procurement)
        .filter(
            Procurement.project_id.in_(
                project_ids
            )
        )
        .all()
    )

    total_procurements = len(
        procurements
    )

    pending_procurements = sum(
        1
        for procurement
        in procurements
        if str(
            procurement.status or ""
        ).upper() != "RECEIVED"
    )

    completed_procurements = sum(
        1
        for procurement
        in procurements
        if str(
            procurement.status or ""
        ).upper() == "RECEIVED"
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "project_progress":
            project_progress,

        "budget": {
            "total_budget":
                total_budget,
            "total_actual_cost":
                total_actual_cost,
            "remaining_budget":
                remaining_budget,
            "utilization_percentage":
                utilization_percentage
        },

        "workforce": {
            "total_workers":
                total_workers,
            "active_allocations":
                active_allocations,
            "present":
                present,
            "absent":
                absent
        },

        "resources": {
            "total_quantity":
                total_quantity,
            "allocated_quantity":
                allocated_quantity,
            "available_quantity":
                available_quantity,
            "utilization":
                utilization
        },

        "procurement": {
            "total_procurements":
                total_procurements,
            "pending_procurements":
                pending_procurements,
            "completed_procurements":
                completed_procurements
        }
    }


# ============================================================
# PROJECT-SPECIFIC DASHBOARD
# ============================================================

@router.get(
    "/project/{project_id}",
    response_model=ProjectDashboardResponse
)
def project_dashboard(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):

    # ========================================================
    # FIND PROJECT
    # ========================================================

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
            detail="Project not found."
        )

    # ========================================================
    # MANAGER ACCESS CONTROL
    # ========================================================
    #
    # ADMIN can access any project.
    # MANAGER can access only their assigned project.
    #

    if (
        current_user.role == "MANAGER"
        and project.manager_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Access Denied: "
                "You are not assigned to this project."
            )
        )

    # ========================================================
    # PROJECT PROGRESS
    # ========================================================

    progress = calculate_project_progress(
        db,
        project.id
    )

    # ========================================================
    # BUDGET
    # ========================================================

    total_budget = float(
        getattr(
            project,
            "budget",
            0
        ) or 0
    )

    # --------------------------------------------------------
    # LABOUR COST
    # --------------------------------------------------------

    payroll_records = (
        db.query(Payroll)
        .filter(
            Payroll.project_id == project.id
        )
        .all()
    )

    actual_labour_cost = sum(
        float(
            payroll.estimated_pay or 0
        )
        for payroll
        in payroll_records
    )

    # --------------------------------------------------------
    # MATERIAL COST
    # --------------------------------------------------------
    #
    # Current Material/Inventory models do not contain
    # price/cost fields.
    #
    # Therefore no artificial material cost is calculated.
    #

    actual_material_cost = 0.0

    # --------------------------------------------------------
    # PROCUREMENT COST
    # --------------------------------------------------------
    #
    # Current Procurement model does not contain
    # unit-price/cost fields.
    #
    # Therefore no artificial procurement cost is calculated.
    #

    actual_procurement_cost = 0.0

    # --------------------------------------------------------
    # MAINTENANCE COST
    # --------------------------------------------------------

    maintenance_records = (
        db.query(Maintenance)
        .join(
            Machinery,
            Maintenance.machinery_id
            == Machinery.id
        )
        .filter(
            Machinery.project_id == project.id
        )
        .all()
    )

    actual_maintenance_cost = sum(
        float(
            maintenance.cost or 0
        )
        for maintenance
        in maintenance_records
    )

    total_actual_cost = round(
        actual_labour_cost
        + actual_material_cost
        + actual_procurement_cost
        + actual_maintenance_cost,
        2
    )

    remaining_budget = round(
        total_budget
        - total_actual_cost,
        2
    )

    budget_utilization_percentage = 0.0

    if total_budget > 0:

        budget_utilization_percentage = round(
            (
                total_actual_cost
                / total_budget
            ) * 100,
            2
        )

    # ========================================================
    # WORKFORCE
    # ========================================================

    worker_assignments = (
        db.query(WorkerAssignment)
        .filter(
            WorkerAssignment.project_id
            == project.id
        )
        .all()
    )

    worker_ids = {
        assignment.worker_id
        for assignment
        in worker_assignments
    }

    total_workers = len(worker_ids)

    active_allocations = (
        db.query(WorkerAssignment)
        .filter(
            WorkerAssignment.project_id
            == project.id,
            WorkerAssignment.assignment_status
            == "ACTIVE"
        )
        .count()
    )

    # ========================================================
    # TODAY'S ATTENDANCE
    # ========================================================

    today = date.today().isoformat()

    present = (
        db.query(Attendance)
        .filter(
            Attendance.project_id == project.id,
            Attendance.date == today,
            Attendance.status == "Present"
        )
        .count()
    )

    absent = (
        db.query(Attendance)
        .filter(
            Attendance.project_id == project.id,
            Attendance.date == today,
            Attendance.status == "Absent"
        )
        .count()
    )

    # ========================================================
    # RESOURCE UTILIZATION
    # ========================================================

    resources = (
        db.query(Resource)
        .filter(
            Resource.project_id == project.id
        )
        .all()
    )

    total_quantity = sum(
        resource.quantity or 0
        for resource in resources
    )

    allocated_quantity = sum(
        resource.allocated_quantity or 0
        for resource in resources
    )

    available_quantity = (
        total_quantity
        - allocated_quantity
    )

    resource_utilization = 0.0

    if total_quantity > 0:

        resource_utilization = round(
            (
                allocated_quantity
                / total_quantity
            ) * 100,
            2
        )

    # ========================================================
    # PROCUREMENT OVERVIEW
    # ========================================================

    procurements = (
        db.query(Procurement)
        .filter(
            Procurement.project_id == project.id
        )
        .all()
    )

    total_procurements = len(
        procurements
    )

    pending_procurements = sum(
        1
        for procurement
        in procurements
        if str(
            procurement.status or ""
        ).upper() != "RECEIVED"
    )

    completed_procurements = sum(
        1
        for procurement
        in procurements
        if str(
            procurement.status or ""
        ).upper() == "RECEIVED"
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "project_id":
            project.id,

        "project_name":
            project.project_name,

        "project_code":
            project.project_code,

        "project_category":
            project.project_category,

        "status":
            project.status,

        "progress":
            progress,

        "budget": {
            "total_budget":
                total_budget,

            "total_actual_cost":
                total_actual_cost,

            "remaining_budget":
                remaining_budget,

            "utilization_percentage":
                budget_utilization_percentage
        },

        "workforce": {
            "total_workers":
                total_workers,

            "active_allocations":
                active_allocations,

            "present":
                present,

            "absent":
                absent
        },

        "resources": {
            "total_quantity":
                total_quantity,

            "allocated_quantity":
                allocated_quantity,

            "available_quantity":
                available_quantity,

            "utilization":
                resource_utilization
        },

        "procurement": {
            "total_procurements":
                total_procurements,

            "pending_procurements":
                pending_procurements,

            "completed_procurements":
                completed_procurements
        }
    }


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get(
    "/admin-dashboard",
    response_model=AdminDashboardResponse
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN"])
    )
):

    # ========================================================
    # USER MANAGEMENT
    # ========================================================

    users = db.query(User).all()

    total_users = len(users)

    active_users = sum(
        1
        for user in users
        if user.is_active
    )

    inactive_users = (
        total_users
        - active_users
    )

    admins = sum(
        1
        for user in users
        if str(
            user.role or ""
        ).upper() == "ADMIN"
    )

    managers = sum(
        1
        for user in users
        if str(
            user.role or ""
        ).upper() == "MANAGER"
    )

    engineers = sum(
        1
        for user in users
        if str(
            user.role or ""
        ).upper() == "ENGINEER"
    )

    clients = sum(
        1
        for user in users
        if str(
            user.role or ""
        ).upper() == "CLIENT"
    )

    # ========================================================
    # PROJECT MONITORING
    # ========================================================

    projects = db.query(Project).all()

    total_projects = len(projects)

    active_projects = sum(
        1
        for project in projects
        if str(
            project.status or ""
        ).upper() == "ACTIVE"
    )

    completed_projects = sum(
        1
        for project in projects
        if str(
            project.status or ""
        ).upper() == "CLOSED"
    )

    pending_projects = (
        total_projects
        - active_projects
        - completed_projects
    )

    # ========================================================
    # REPORTS MANAGEMENT
    # ========================================================

    reports = db.query(Report).all()

    total_reports = len(reports)

    completed_reports = sum(
        1
        for report in reports
        if str(
            report.status or ""
        ).upper() == "COMPLETED"
    )

    pending_reports = (
        total_reports
        - completed_reports
    )

    # ========================================================
    # SYSTEM ANALYTICS
    # ========================================================

    total_workers = (
        db.query(Worker).count()
    )

    total_resources = (
        db.query(Resource).count()
    )

    total_inventory_items = (
        db.query(Inventory).count()
    )

    total_procurements = (
        db.query(Procurement).count()
    )

    total_milestones = (
        db.query(ProjectMilestone).count()
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "users": {
            "total_users":
                total_users,
            "active_users":
                active_users,
            "inactive_users":
                inactive_users,
            "admins":
                admins,
            "managers":
                managers,
            "engineers":
                engineers,
            "clients":
                clients
        },

        "projects": {
            "total_projects":
                total_projects,
            "active_projects":
                active_projects,
            "completed_projects":
                completed_projects,
            "pending_projects":
                pending_projects
        },

        "reports": {
            "total_reports":
                total_reports,
            "completed_reports":
                completed_reports,
            "pending_reports":
                pending_reports
        },

        "system": {
            "total_workers":
                total_workers,
            "total_resources":
                total_resources,
            "total_inventory_items":
                total_inventory_items,
            "total_procurements":
                total_procurements,
            "total_milestones":
                total_milestones
        }
    }


# ============================================================
# ACTIVITY MONITORING
# ============================================================

@router.get(
    "/activity-monitoring",
    response_model=ActivityMonitoringResponse
)
def activity_monitoring(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN"])
    )
):

    activities = (
        db.query(SiteActivityLog)
        .all()
    )

    total_activity_logs = len(
        activities
    )

    today = date.today()

    today_activity_logs = sum(
        1
        for activity
        in activities
        if activity.activity_date == today
    )

    # ========================================================
    # ACTIVITY TYPE SUMMARY
    # ========================================================

    activity_type_counts = {}

    for activity in activities:

        activity_type = (
            activity.activity_type
            or "UNKNOWN"
        )

        activity_type_counts[
            activity_type
        ] = (
            activity_type_counts.get(
                activity_type,
                0
            ) + 1
        )

    activity_by_type = [
        {
            "activity_type":
                activity_type,
            "count":
                count
        }
        for activity_type, count
        in activity_type_counts.items()
    ]

    # ========================================================
    # PROJECT ACTIVITY SUMMARY
    # ========================================================

    project_activity_counts = {}

    for activity in activities:

        project_id = (
            activity.project_id
        )

        project_activity_counts[
            project_id
        ] = (
            project_activity_counts.get(
                project_id,
                0
            ) + 1
        )

    activity_by_project = []

    for project_id, count in (
        project_activity_counts.items()
    ):

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id
            )
            .first()
        )

        if project:

            activity_by_project.append(
                {
                    "project_id":
                        project.id,
                    "project_name":
                        project.project_name,
                    "count":
                        count
                }
            )

    # ========================================================
    # RECENT ACTIVITIES
    # ========================================================

    sorted_activities = sorted(
        activities,
        key=lambda activity: (
            activity.activity_date,
            activity.activity_time
        ),
        reverse=True
    )

    recent_activities = []

    for activity in sorted_activities[:10]:

        project = (
            db.query(Project)
            .filter(
                Project.id
                == activity.project_id
            )
            .first()
        )

        project_name = (
            project.project_name
            if project
            else "Unknown Project"
        )

        recent_activities.append(
            {
                "id":
                    activity.id,
                "project_id":
                    activity.project_id,
                "project_name":
                    project_name,
                "activity_date":
                    str(
                        activity.activity_date
                    ),
                "activity_time":
                    str(
                        activity.activity_time
                    ),
                "activity_type":
                    activity.activity_type,
                "description":
                    activity.description,
                "responsible_person":
                    activity.responsible_person
            }
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "total_activity_logs":
            total_activity_logs,

        "today_activity_logs":
            today_activity_logs,

        "activity_by_type":
            activity_by_type,

        "activity_by_project":
            activity_by_project,

        "recent_activities":
            recent_activities
    }
