from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_type: str | None = None
    file_size: int | None = None
    category: str
    description: str | None = None
    project_id: int | None = None
    uploaded_by: int | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True