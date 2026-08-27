from pydantic import BaseModel, ConfigDict


class PurchaseOrderItemCreate(BaseModel):
    purchase_order_id: int
    item_name: str
    category: str
    quantity: int
    unit_price: float


class PurchaseOrderItemResponse(PurchaseOrderItemCreate):
    id: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)
