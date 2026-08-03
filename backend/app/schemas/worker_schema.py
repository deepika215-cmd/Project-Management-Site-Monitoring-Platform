from pydantic import BaseModel


class WorkerCreate(BaseModel):
    name: str
    role: str
    phone: str
    address: str
    project_id: int


class WorkerResponse(BaseModel):
    id: int
    name: str
    role: str
    phone: str
    address: str
    project_id: int

    class Config:
        from_attributes = True