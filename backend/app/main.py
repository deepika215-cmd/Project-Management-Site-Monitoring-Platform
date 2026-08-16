from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# Import Models

from app.models.user import User
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.resource import Resource
from app.models.machinery import Machinery
from app.models.maintenance import Maintenance
from app.models.inventory import Inventory
from app.models.worker import Worker
from app.models.attendance import Attendance
from app.models.procurement import Procurement
from app.models.notification import Notification
from app.models.report import Report

# Import Routers

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.project import router as project_router
from app.api.milestone import router as milestone_router
from app.api.resource import router as resource_router
from app.api.machinery import router as machinery_router
from app.api.maintenance import router as maintenance_router
from app.api.inventory import router as inventory_router
from app.api.worker import router as worker_router
from app.api.attendance import router as attendance_router
from app.api.procurement import router as procurement_router
from app.api.notification import router as notification_router
from app.api.report import router as report_router
from app.api.analytics import router as analytics_router
from app.api.daily_progress import router as daily_progress_router
from app.api.weekly_progress import router as weekly_progress_router
from app.api.delay_record import router as delay_record_router
from app.api.progress_photo import router as progress_photo_router
from app.api.material import router as material_router
from app.api.material_request import router as material_request_router
from app.api.material_allocation import router as material_allocation_router
from app.api.stock_movement import router as stock_movement_router


# Create all database tables

Base.metadata.create_all(bind=engine)


# Create FastAPI application

app = FastAPI(title="BuildTrack API")


# CORS Configuration

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API Routers

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(milestone_router)
app.include_router(resource_router)
app.include_router(machinery_router)
app.include_router(maintenance_router)
app.include_router(inventory_router)
app.include_router(worker_router)
app.include_router(attendance_router)
app.include_router(procurement_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(analytics_router)
app.include_router(daily_progress_router)
app.include_router(weekly_progress_router)
app.include_router(delay_record_router)
app.include_router(progress_photo_router)
app.include_router(material_router)
app.include_router(material_request_router)
app.include_router(material_allocation_router)
app.include_router(stock_movement_router)


# Home Route

@app.get("/")
def home():
    return {
        "message": "BuildTrack Backend Running Successfully"
    }