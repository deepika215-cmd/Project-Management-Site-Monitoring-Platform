from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectHistoryResponse(BaseModel):
    id: int
    project_id: int
    changed_by: int
    action: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    changed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )