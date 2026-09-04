from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine


# ============================================================
# IMPORT MODELS
# ============================================================

from app.models.user import User
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.task import Task

from app.models.resource import Resource
from app.models.resource_category import ResourceCategory
from app.models.resource_allocation import ResourceAllocation
from app.models.resource_utilization import ResourceUtilization
from app.models.machinery import Machinery
from app.models.maintenance import Maintenance
from app.models.inventory import Inventory
from app.models.document import Document


# ============================================================
# WORKFORCE MANAGEMENT MODELS
# ============================================================

from app.models.worker import Worker
from app.models.contractor import Contractor
from app.models.worker_assignment import WorkerAssignment
from app.models.workforce_category import WorkforceCategory
from app.models.attendance import Attendance
from app.models.shift import Shift
from app.models.payroll import Payroll


# ============================================================
# OTHER MODELS
# ============================================================

from app.models.procurement import Procurement
from app.models.notification import Notification
from app.models.report import Report


# ============================================================
# MODULE 3 — SITE PROGRESS MONITORING MODELS
# ============================================================

from app.models.daily_progress import DailyProgress
from app.models.weekly_progress import WeeklyProgress
from app.models.delay_record import DelayRecord
from app.models.progress_photo import ProgressPhoto
from app.models.site_activity_log import SiteActivityLog


# ============================================================
# IMPORT ROUTERS
# ============================================================

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.project import router as project_router
from app.api.milestone import router as milestone_router


# ============================================================
# PROJECT ENGINEER ASSIGNMENT
# ============================================================

from app.api.project_engineer_assignment import (
    router as project_engineer_assignment_router
)


# ============================================================
# TASK MANAGEMENT — MODULE 8
# ============================================================

from app.api.task import router as task_router


# ============================================================
# RESOURCE MANAGEMENT
# ============================================================

from app.api.resource import router as resource_router

from app.api.resource_category import (
    router as resource_category_router
)

from app.api.resource_allocation import (
    router as resource_allocation_router
)

from app.api.resource_utilization import (
    router as resource_utilization_router
)

from app.api.machinery import router as machinery_router
from app.api.maintenance import router as maintenance_router
from app.api.inventory import router as inventory_router


# ============================================================
# WORKFORCE MANAGEMENT ROUTERS
# ============================================================

from app.api.worker import router as worker_router
from app.api.contractor import router as contractor_router
from app.api.worker_assignment import (
    router as worker_assignment_router
)
from app.api.workforce_category import (
    router as workforce_category_router
)
from app.api.attendance import router as attendance_router
from app.api.shift import router as shift_router
from app.api.payroll import router as payroll_router


# ============================================================
# OTHER ROUTERS
# ============================================================

from app.api.procurement import router as procurement_router
from app.api.notification import router as notification_router
from app.api.report import router as report_router


# ============================================================
# ANALYTICS
# ============================================================

from app.api.analytics import router as analytics_router


# ============================================================
# MODULE 3 — SITE PROGRESS MONITORING ROUTERS
# ============================================================

from app.api.daily_progress import router as daily_progress_router
from app.api.weekly_progress import router as weekly_progress_router
from app.api.delay_record import router as delay_record_router
from app.api.progress_photo import router as progress_photo_router
from app.api.site_activity_log import router as site_activity_log_router


# ============================================================
# MATERIAL & INVENTORY MANAGEMENT ROUTERS
# ============================================================

from app.api.material import router as material_router
from app.api.material_request import (
    router as material_request_router
)
from app.api.material_allocation import (
    router as material_allocation_router
)
from app.api.stock_movement import (
    router as stock_movement_router
)


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

from app.api.document import router as document_router


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="BuildTrack API"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REGISTER API ROUTERS
# ============================================================

app.include_router(users_router)
app.include_router(auth_router)


# ============================================================
# PROJECT MANAGEMENT
# ============================================================

app.include_router(project_router)
app.include_router(project_engineer_assignment_router)
app.include_router(milestone_router)


# ============================================================
# TASK MANAGEMENT — MODULE 8
# ============================================================

app.include_router(task_router)


# ============================================================
# RESOURCE MANAGEMENT
# ============================================================

app.include_router(resource_router)
app.include_router(resource_category_router)
app.include_router(resource_allocation_router)
app.include_router(resource_utilization_router)
app.include_router(machinery_router)
app.include_router(maintenance_router)


# ============================================================
# INVENTORY MANAGEMENT
# ============================================================

app.include_router(inventory_router)


# ============================================================
# WORKFORCE MANAGEMENT — MODULE 6
# ============================================================

app.include_router(workforce_category_router)
app.include_router(contractor_router)
app.include_router(worker_router)
app.include_router(worker_assignment_router)
app.include_router(attendance_router)
app.include_router(shift_router)
app.include_router(payroll_router)


# ============================================================
# OTHER MODULES
# ============================================================

app.include_router(procurement_router)
app.include_router(notification_router)
app.include_router(report_router)


# ============================================================
# ANALYTICS
# ============================================================

app.include_router(analytics_router)


# ============================================================
# MODULE 3 — SITE PROGRESS MONITORING
# ============================================================

app.include_router(daily_progress_router)
app.include_router(weekly_progress_router)
app.include_router(delay_record_router)
app.include_router(progress_photo_router)
app.include_router(site_activity_log_router)


# ============================================================
# MATERIAL & INVENTORY MANAGEMENT
# ============================================================

app.include_router(material_router)
app.include_router(material_request_router)
app.include_router(material_allocation_router)
app.include_router(stock_movement_router)


# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

app.include_router(document_router)


# ============================================================
# HOME ROUTE
# ============================================================

@app.get("/")
def home():
    return {
        "message": "BuildTrack Backend Running Successfully"
    }