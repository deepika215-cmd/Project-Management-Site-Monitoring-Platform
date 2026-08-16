from datetime import date
from pydantic import BaseModel


class MaterialAllocationCreate(BaseModel):
    project_id: int
    material_id: int
    quantity: int
    allocation_date: date
    work_activity: str
    responsible_user: str | None = None


class MaterialAllocationResponse(MaterialAllocationCreate):
    id: int
    status: str

    class Config:
        from_attributes = True