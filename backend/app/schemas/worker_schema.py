from pydantic import BaseModel


class WorkerCreate(BaseModel):
    name: str
    role: str
    phone: str
    email: str
    status: str = "Active"


class WorkerResponse(WorkerCreate):
    id: int

    class Config:
        from_attributes = True



