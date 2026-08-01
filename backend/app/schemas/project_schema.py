from datetime import date
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_name: str
    description: str
    location: str
    start_date: date
    end_date: date
    budget: int
    status: str
    manager_id: int


class ProjectResponse(BaseModel):
    id: int
    project_name: str
    description: str
    location: str
    start_date: date
    end_date: date
    budget: int
    status: str
    manager_id: int

    class Config:
        from_attributes = True
