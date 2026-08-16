from datetime import date
from pydantic import BaseModel


class MaterialRequestCreate(BaseModel):
    project_id: int
    material_id: int
    quantity: int
    required_date: date
    purpose: str
    remarks: str | None = None


class MaterialRequestResponse(MaterialRequestCreate):
    id: int
    status: str

    class Config:
        from_attributes = True
