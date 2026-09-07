from pydantic import BaseModel, ConfigDict
from typing import Optional


# ============================================================
# CREATE ATTENDANCE
# ============================================================

class AttendanceCreate(BaseModel):
    worker_id: int
    project_id: Optional[int] = None
    date: str
    status: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    working_hours: float = 0.0
    remarks: Optional[str] = None


# ============================================================
# ATTENDANCE RESPONSE
# ============================================================

class AttendanceResponse(AttendanceCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# ATTENDANCE SUMMARY RESPONSE
# ============================================================

class AttendanceSummaryResponse(BaseModel):
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    half_day_count: int
    total_working_hours: float
    attendance_percentage: float