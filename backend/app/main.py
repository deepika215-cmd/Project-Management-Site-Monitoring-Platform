from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.daily_progress import router as daily_progress_router
from app.api.weekly_progress import router as weekly_progress_router
from app.api.project_milestone import router as milestone_router
from app.api.delay_record import router as delay_record_router
from app.api.site_activity_log import router as site_activity_log_router
from app.api.progress_photo import router as progress_photo_router
from app.api.project import router as project_router

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

@app.get("/test-db")
def test_db():
    return {"database": "SQLite connected successfully"}