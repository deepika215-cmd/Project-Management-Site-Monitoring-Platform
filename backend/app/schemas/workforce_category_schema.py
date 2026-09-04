from pydantic import BaseModel, ConfigDict


class WorkforceCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    status: str = "Active"


class WorkforceCategoryResponse(WorkforceCategoryCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )