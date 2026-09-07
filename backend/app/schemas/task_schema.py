from datetime import date

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    status: str = "Pending"
    project_id: int
    assigned_to: int


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    due_date: date | None
    status: str
    project_id: int
    assigned_to: int

    model_config = ConfigDict(
        from_attributes=True
    )