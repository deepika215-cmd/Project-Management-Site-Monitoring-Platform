from pydantic import BaseModel, ConfigDict


class AttendanceCreate(BaseModel):
    worker_id: int
    date: str
    status: str


class AttendanceResponse(AttendanceCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)