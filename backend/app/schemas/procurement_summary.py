from pydantic import BaseModel


class ProcurementSummary(BaseModel):
    procurement_id: int
    item_name: str
    supplier: str
    quantity: int
    status: str