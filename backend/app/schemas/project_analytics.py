from pydantic import BaseModel


class ProjectAnalytics(BaseModel):
    project_id: int
    project_name: str
    status: str
    progress: float