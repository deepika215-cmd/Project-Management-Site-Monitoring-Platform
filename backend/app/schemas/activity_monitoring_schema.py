from pydantic import BaseModel


class ActivityTypeSummary(BaseModel):
    activity_type: str
    count: int


class ProjectActivitySummary(BaseModel):
    project_id: int
    project_name: str
    count: int


class RecentActivity(BaseModel):
    id: int
    project_id: int
    project_name: str
    activity_date: str
    activity_time: str
    activity_type: str
    description: str
    responsible_person: str


class ActivityMonitoringResponse(BaseModel):
    total_activity_logs: int
    today_activity_logs: int
    activity_by_type: list[ActivityTypeSummary]
    activity_by_project: list[ProjectActivitySummary]
    recent_activities: list[RecentActivity]
