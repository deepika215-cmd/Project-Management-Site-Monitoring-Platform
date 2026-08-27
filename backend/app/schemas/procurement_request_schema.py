from datetime import date
from pydantic import BaseModel, ConfigDict


class ProcurementRequestCreate(BaseModel):
    project_id: int
    requested_by: int
    item_name: str
    category: str
    quantity: int
    required_date: date
    purpose: str
    priority: str = "NORMAL"
    request_date: date
    remarks: str | None = None


class ProcurementRequestResponse(ProcurementRequestCreate):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
