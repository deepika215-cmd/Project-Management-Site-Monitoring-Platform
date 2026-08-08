from pydantic import BaseModel


class InventoryCreate(BaseModel):
    material_name: str
    quantity: int
    unit: str
    supplier: str
    status: str


class InventoryResponse(InventoryCreate):
    id: int

    class Config:
        from_attributes = True