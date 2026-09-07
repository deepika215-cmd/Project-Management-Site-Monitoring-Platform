from datetime import date
from pydantic import BaseModel, Field


class ProjectScheduleCreate(BaseModel):
    project_id: int
    activity_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date
    end_date: date
    dependency: str | None = None
    status: str = "Not Started"


class ProjectScheduleUpdate(BaseModel):
    activity_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date
    end_date: date
    dependency: str | None = None
    status: str = "Not Started"
