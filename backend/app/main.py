from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# Import Models

from app.models.user import User
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.resource import Resource
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
from app.api.inventory import router as inventory_router
from app.api.worker import router as worker_router
from app.api.attendance import router as attendance_router
from app.api.procurement import router as procurement_router
from app.api.notification import router as notification_router
from app.api.report import router as report_router
from app.api.analytics import router as analytics_router


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
app.include_router(inventory_router)
app.include_router(worker_router)
app.include_router(attendance_router)
app.include_router(procurement_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(analytics_router)


# Home Route

@app.get("/")
def home():
    return {
        "message": "BuildTrack Backend Running Successfully"
    }

