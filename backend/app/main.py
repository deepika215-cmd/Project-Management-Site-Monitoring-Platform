from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.api.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BuildTrack API")

app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "BuildTrack Backend Running Successfully"}