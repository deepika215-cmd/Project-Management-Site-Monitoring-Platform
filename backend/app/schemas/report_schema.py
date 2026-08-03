from pydantic import BaseModel
from typing import Optional


class ReportCreate(BaseModel):
    title: str
    description: Optional[str] = None
    report_type: Optional[str] = None
    status: Optional[str] = None


class ReportResponse(ReportCreate):
    id: int

    class Config:
        from_attributes = True