from pydantic import BaseModel


class WorkerAnalytics(BaseModel):
    worker_id: int
    worker_name: str
    present_days: int
    absent_days: int
    attendance_percentage: float