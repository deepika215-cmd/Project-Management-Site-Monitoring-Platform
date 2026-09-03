from datetime import date
from pydantic import BaseModel


class DailyProgressCreate(BaseModel):
    project_id: int
    milestone_id: int | None = None

    report_date: date

    work_category: str

    activity: str

    completion_percentage: float

    contractor_name: str

    workers_present: int

    workers_absent: int

    machinery_used: str

    materials_used: str

    weather: str

    safety_observation: str

    quality_remarks: str

    quality_verified: bool = False

    delay_hours: float

    delay_reason: str

    comments: str


class DailyProgressResponse(DailyProgressCreate):
    id: int

    class Config:
        from_attributes = True