from pydantic import BaseModel, ConfigDict
from typing import Optional


class ShiftCreate(BaseModel):
    worker_id: int
    project_id: int

    shift_name: str

    shift_date: str

    start_time: str
    end_time: str

    shift_type: str = "REGULAR"

    status: str = "SCHEDULED"

    remarks: Optional[str] = None


class ShiftResponse(ShiftCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )
