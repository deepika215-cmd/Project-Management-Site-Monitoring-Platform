from pydantic import BaseModel


class ProjectSummary(BaseModel):
    total: int
    active: int
    completed: int
    pending: int


class WorkerSummary(BaseModel):
    total: int
    present: int
    absent: int


class ResourceSummary(BaseModel):
    total: int


class InventorySummary(BaseModel):
    total: int


class ProcurementSummary(BaseModel):
    total: int


class AnalyticsResponse(BaseModel):
    projects: ProjectSummary
    workers: WorkerSummary
    resources: ResourceSummary
    inventory: InventorySummary
    procurements: ProcurementSummary


class ResourceUtilization(BaseModel):
    resource_id: int
    resource_name: str
    available: int
    allocated: int
    utilization: float