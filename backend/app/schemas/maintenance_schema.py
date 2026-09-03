from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MaintenanceCreate(BaseModel):
    machinery_id: int
    maintenance_type: str
    description: Optional[str] = None
    scheduled_date: date
    completion_date: Optional[date] = None
    status: str = "Scheduled"
    cost: float = Field(default=0, ge=0)
    technician: Optional[str] = None


class MaintenanceResponse(BaseModel):
    id: int
    machinery_id: int
    maintenance_type: str
    description: Optional[str]
    scheduled_date: date
    completion_date: Optional[date]
    status: str
    cost: float
    technician: Optional[str]

    class Config:
        from_attributes = True


class MaintenanceStatusUpdate(BaseModel):
    status: str


class MaintenanceCompletion(BaseModel):
    completion_date: date
