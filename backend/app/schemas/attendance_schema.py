from pydantic import BaseModel, ConfigDict
from typing import Optional


class AttendanceCreate(BaseModel):
    worker_id: int
    project_id: Optional[int] = None
    date: str
    status: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    working_hours: float = 0.0
    remarks: Optional[str] = None


class AttendanceResponse(AttendanceCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)