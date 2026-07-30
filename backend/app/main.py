from fastapi import FastAPI

from app.database.database import Base, engine

# Import Models
from app.models.user import User
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.resource import Resource
from app.models.inventory import Inventory
from app.models.worker import Worker
from app.models.attendance import Attendance

# Import Routers
from app.api.auth import router as auth_router

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(title="BuildTrack API")

# Register API Routers
app.include_router(auth_router)

# Home Route
@app.get("/")
def home():
    return {
        "message": "BuildTrack Backend Running Successfully"
    }