from pydantic import BaseModel


class ReportAnalytics(BaseModel):
    report_id: int
    title: str
    report_type: str
    status: str