from pydantic import BaseModel


class ResourceCreate(BaseModel):
    name: str
    type: str
    quantity: int
    status: str
    project_id: int


class ResourceResponse(BaseModel):
    id: int
    name: str
    type: str
    quantity: int
    status: str
    project_id: int

    class Config:
        from_attributes = True