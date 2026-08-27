from datetime import date
from pydantic import BaseModel, ConfigDict


class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    project_id: int
    procurement_request_id: int
    order_date: date
    expected_delivery_date: date | None = None
    total_amount: float = 0
    tax_amount: float = 0
    additional_charges: float = 0
    overall_amount: float = 0
    status: str = "Processing"


class PurchaseOrderResponse(PurchaseOrderCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
