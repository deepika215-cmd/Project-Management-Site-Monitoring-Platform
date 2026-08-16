from datetime import datetime
from pydantic import BaseModel


class ProgressPhotoCreate(BaseModel):
    project_id: int
    daily_progress_id: int | None = None
    photo_url: str
    description: str | None = None


class ProgressPhotoResponse(ProgressPhotoCreate):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
