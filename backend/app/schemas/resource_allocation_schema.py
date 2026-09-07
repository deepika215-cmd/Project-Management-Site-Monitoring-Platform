from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ResourceAllocationCreate(BaseModel):
    resource_id: int
    project_id: int
    worker_id: int
    quantity: int = Field(gt=0)
    allocation_date: date
    expected_return_date: date


class ResourceAllocationResponse(BaseModel):
    id: int
    resource_id: int
    project_id: int
    worker_id: Optional[int] = None
    quantity: int
    allocation_date: date
    expected_return_date: date
    actual_return_date: Optional[date]
    responsible_person: str
    status: str

    class Config:
        from_attributes = True