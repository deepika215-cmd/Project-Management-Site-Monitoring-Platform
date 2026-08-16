from datetime import datetime
from pydantic import BaseModel


class StockMovementCreate(BaseModel):
    material_id: int
    project_id: int | None = None
    movement_type: str
    quantity: int
    remarks: str | None = None


class StockMovementResponse(StockMovementCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
