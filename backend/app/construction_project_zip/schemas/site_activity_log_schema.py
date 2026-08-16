from datetime import date, time
from pydantic import BaseModel


class SiteActivityLogCreate(BaseModel):
    project_id: int
    activity_date: date
    activity_time: time | None = None
    activity_type: str
    description: str
    responsible_person: str


class SiteActivityLogResponse(SiteActivityLogCreate):
    id: int

    class Config:
        from_attributes = True
