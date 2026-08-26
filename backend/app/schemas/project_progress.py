from pydantic import BaseModel


class ProjectProgress(BaseModel):
    project_id: int
    project_name: str
    total_milestones: int
    completed_milestones: int
    progress: float