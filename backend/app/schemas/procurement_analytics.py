from pydantic import BaseModel


class ProcurementAnalytics(BaseModel):
    procurement_id: int
    item_name: str
    supplier: str
    ordered: int
    received: int
    pending: int