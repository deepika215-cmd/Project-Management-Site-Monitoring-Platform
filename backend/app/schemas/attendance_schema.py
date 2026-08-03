from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    worker_id: int
    date: str
    status: str


class AttendanceResponse(AttendanceCreate):
    id: int

    class Config:
        from_attributes = True