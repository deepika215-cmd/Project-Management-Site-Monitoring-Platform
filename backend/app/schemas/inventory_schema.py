from pydantic import BaseModel


# ============================================================
# INVENTORY RESPONSE
# ============================================================

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


# ============================================================
# INVENTORY STATUS RESPONSE
# ============================================================

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


# ============================================================
# LOW STOCK ALERT RESPONSE
# ============================================================

class LowStockAlertResponse(BaseModel):
    id: int
    item_name: str
    category: str
    available_stock: int
    minimum_stock: int
    unit: str | None = None
    supplier: str | None = None
    project_id: int | None = None
    alert_status: str
    message: str