from pydantic import BaseModel, ConfigDict
from typing import Optional


# ============================================================
# CREATE / UPDATE PAYROLL
# ============================================================

class PayrollCreate(BaseModel):
    worker_id: int
    project_id: Optional[int] = None

    pay_rate: float = 0.0

    working_days: int = 0
    working_hours: float = 0.0
    overtime_hours: float = 0.0
    leave_days: int = 0

    estimated_pay: float = 0.0

    payroll_status: str = "PENDING"


# ============================================================
# PAYROLL RESPONSE
# ============================================================

class PayrollResponse(PayrollCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )
