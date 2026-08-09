from datetime import date
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_name: str
    description: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget: int | None = None
    status: str = "Planning"
    completion_percentage: float = 0.0
    manager_id: int | None = None


class ProjectResponse(ProjectCreate):
    id: int

    class Config:
        from_attributes = True