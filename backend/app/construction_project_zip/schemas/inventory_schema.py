from pydantic import BaseModel


class InventoryResponse(BaseModel):
    id: int
    item_name: str
    category: str
    quantity: int
    unit: str | None = None
    supplier: str | None = None
    project_id: int | None = None

    class Config:
        from_attributes = True


class InventoryStatusResponse(BaseModel):
    id: int
    item_name: str
    category: str
    total_stock: int
    allocated_stock: int
    consumed_stock: int
    available_stock: int
    unit: str | None = None
    minimum_stock: int
    available_status: str