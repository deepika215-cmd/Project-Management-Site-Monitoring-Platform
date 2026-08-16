from datetime import date
from pydantic import BaseModel


class DelayRecordCreate(BaseModel):
    project_id: int
    delay_date: date
    reason: str
    duration_hours: int
    affected_work: str
    impact: str


class DelayRecordResponse(DelayRecordCreate):
    id: int

    class Config:
        from_attributes = True