from pydantic import BaseModel


class ProcurementCreate(BaseModel):
    item_name: str
    quantity: int
    supplier: str
    status: str = "Available"
    project_id: int


class ProcurementResponse(ProcurementCreate):
    id: int
    used: int

    class Config:
        from_attributes = True


class ProcurementUsage(BaseModel):
    quantity: int


class ProcurementUtilization(BaseModel):
    procurement_id: int
    item_name: str
    total_quantity: int
    used_quantity: int
    available_quantity: int
    utilization_percentage: float
    status: str