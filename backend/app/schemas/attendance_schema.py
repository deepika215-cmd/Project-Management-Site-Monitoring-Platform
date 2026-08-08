from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    worker_id: int
    date: str
    status: str


class AttendanceResponse(AttendanceCreate):
    id: int
    used: int

    class Config:
        from_attributes = True


# Used when marking attendance as used/released
class AttendanceUsage(BaseModel):
    quantity: int


# Response for attendance utilization
class AttendanceUtilization(BaseModel):
    attendance_id: int
    worker_id: int
    date: str
    status: str
    used_quantity: int
    available_quantity: int
    utilization_percentage: float