from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.daily_progress import router as daily_progress_router
from app.api.weekly_progress import router as weekly_progress_router
from app.api.project_milestone import router as milestone_router
from app.api.delay_record import router as delay_record_router
from app.api.site_activity_log import router as site_activity_log_router
from app.api.progress_photo import router as progress_photo_router
from app.api.project import router as project_router
from app.api.material import router as material_router
from app.api.material_request import router as material_request_router
from app.api.material_allocation import router as material_allocation_router
from app.api.stock_movement import router as stock_movement_router
from app.api.inventory import router as inventory_router

from app.database.database import Base, engine
import app.database.base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Project Management API")

app.include_router(auth_router)
app.include_router(daily_progress_router)
app.include_router(weekly_progress_router)
app.include_router(milestone_router)
app.include_router(delay_record_router)
app.include_router(site_activity_log_router)
app.include_router(progress_photo_router)
app.include_router(project_router)
app.include_router(material_router)
app.include_router(material_request_router)
app.include_router(material_allocation_router)
app.include_router(stock_movement_router)
app.include_router(inventory_router)

@app.get("/test-db")
def test_db():
    return {"database": "SQLite connected successfully"}