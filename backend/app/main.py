from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.daily_progress import router as daily_progress_router
from app.api.weekly_progress import router as weekly_progress_router

from app.database.database import Base, engine
import app.database.base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Project Management API")

app.include_router(auth_router)
app.include_router(daily_progress_router)
app.include_router(weekly_progress_router)

@app.get("/test-db")
def test_db():
    return {"database": "SQLite connected successfully"}