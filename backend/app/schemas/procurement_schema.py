from pydantic import BaseModel, ConfigDict


class ProcurementCreate(BaseModel):
    item_name: str
    quantity: int
    supplier: str
    status: str
    project_id: int


class ProcurementResponse(ProcurementCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)