from datetime import date
from pydantic import BaseModel


class MilestoneCreate(BaseModel):
    title: str
    description: str
    due_date: date
    status: str
    project_id: int


class MilestoneResponse(BaseModel):
    id: int
    title: str
    description: str
    due_date: date
    status: str
    project_id: int

    class Config:
        from_attributes = True