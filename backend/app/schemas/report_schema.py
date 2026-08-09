from typing import Optional

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: Optional[str] = None
    status: Optional[str] = None


class ReportResponse(ReportCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)