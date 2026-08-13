from pydantic import BaseModel, Field
from typing import Optional


class MachineryCreate(BaseModel):
    name: str
    machinery_type: str
    location: Optional[str] = None
    status: str = "Available"
    operator: Optional[str] = None
    hours_used: float = Field(default=0, ge=0)
    project_id: Optional[int] = None


class MachineryResponse(BaseModel):
    id: int
    name: str
    machinery_type: str
    location: Optional[str]
    status: str
    operator: Optional[str]
    hours_used: float
    project_id: Optional[int]

    class Config:
        from_attributes = True


class MachineryStatusUpdate(BaseModel):
    status: str


class MachineryHoursUpdate(BaseModel):
    hours: float = Field(gt=0)
