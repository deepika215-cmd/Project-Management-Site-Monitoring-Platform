from pydantic import BaseModel, ConfigDict


class WorkerAssignmentCreate(BaseModel):
    worker_id: int
    contractor_id: int
    project_id: int
    work_activity: str | None = None
    assignment_start_date: str
    assignment_end_date: str | None = None
    assignment_status: str = "ACTIVE"


class WorkerAssignmentResponse(WorkerAssignmentCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )