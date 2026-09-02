from pydantic import BaseModel, ConfigDict


class ProcurementCreate(BaseModel):
    item_name: str
    quantity: int
    supplier: str
    status: str
    project_id: int


class ProcurementResponse(ProcurementCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class ProcurementReportResponse(BaseModel):
    total_requests: int
    pending_count: int
    approved_count: int
    rejected_count: int
    completed_count: int
    total_quantity: int
    used_quantity: int
    remaining_quantity: int
