from datetime import date, time

from pydantic import BaseModel, ConfigDict


class SiteActivityLogCreate(BaseModel):
    project_id: int
    activity_date: date
    activity_time: time
    activity_type: str
    description: str
    responsible_person: str


class SiteActivityLogResponse(SiteActivityLogCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)