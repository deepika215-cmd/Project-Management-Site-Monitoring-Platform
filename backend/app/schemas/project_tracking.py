from pydantic import BaseModel


class ProjectTrackingResponse(BaseModel):
    project_id: int
    project_name: str
    status: str

    total_milestones: int
    completed_milestones: int
    pending_milestones: int

    progress: float