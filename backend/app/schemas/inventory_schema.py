from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    material_name: str
    quantity: int = Field(ge=0)
    unit: str
    supplier: str
    status: str


class InventoryResponse(InventoryCreate):
    id: int
    used: int

    class Config:
        from_attributes = True


class InventoryUsage(BaseModel):
    quantity: int = Field(gt=0)


class InventoryUtilization(BaseModel):
    inventory_id: int
    material_name: str
    total_quantity: int
    used_quantity: int
    available_quantity: int
    utilization_percentage: float
    status: str