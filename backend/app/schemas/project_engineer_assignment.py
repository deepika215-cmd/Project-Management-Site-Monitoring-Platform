from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectEngineerAssignmentCreate(BaseModel):
    engineer_id: int


class ProjectEngineerAssignmentResponse(BaseModel):
    id: int
    project_id: int
    engineer_id: int
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)