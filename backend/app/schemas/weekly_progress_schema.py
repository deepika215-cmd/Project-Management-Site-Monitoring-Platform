from datetime import date
from pydantic import BaseModel


class WeeklyProgressCreate(BaseModel):
    project_id: int
    week_start: date
    week_end: date
    work_completed: str
    completion_percentage: float
    worker_hours: int
    major_activities: str
    delays: str
    safety_incidents: str
    overall_status: str


class WeeklyProgressResponse(WeeklyProgressCreate):
    id: int

    class Config:
        from_attributes = True