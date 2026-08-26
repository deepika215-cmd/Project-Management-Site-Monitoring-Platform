from pydantic import BaseModel, ConfigDict


class ProcurementRequestItemCreate(BaseModel):
    procurement_request_id: int
    item_name: str
    category: str
    quantity: int
    estimated_unit_price: float = 0
    estimated_total_price: float = 0
    remarks: str | None = None


class ProcurementRequestItemResponse(ProcurementRequestItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)