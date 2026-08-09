from datetime import date
from pydantic import BaseModel


class ProjectMilestoneCreate(BaseModel):

    title: str
    description: str | None = None
    due_date: date | None = None
    status: str = "Pending"
    completion_percentage: float = 0.0
    project_id: int


class ProjectMilestoneResponse(ProjectMilestoneCreate):

    id: int

    class Config:
        from_attributes = True