from pydantic import BaseModel, ConfigDict


class WorkerCreate(BaseModel):
    name: str
    role: str
    phone: str | None = None
    email: str | None = None

    category: str = "Skilled Worker"

    skill_type: str | None = None

    contractor_id: int | None = None

    joining_date: str | None = None

    status: str = "Active"


class WorkerResponse(WorkerCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )