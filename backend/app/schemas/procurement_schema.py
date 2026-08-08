from pydantic import BaseModel


class ProcurementCreate(BaseModel):
    item_name: str
    quantity: int
    supplier: str
    status: str
    project_id: int


class ProcurementResponse(ProcurementCreate):
    id: int

    class Config:
        from_attributes = True