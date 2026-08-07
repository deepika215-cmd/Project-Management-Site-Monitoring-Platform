from pydantic import BaseModel


class ProjectAnalytics(BaseModel):
    total: int
    active: int
    completed: int
    pending: int


class WorkerAnalytics(BaseModel):
    total: int
    present: int
    absent: int


class ResourceAnalytics(BaseModel):
    total: int


class InventoryAnalytics(BaseModel):
    total: int


class ProcurementAnalytics(BaseModel):
    total: int


class AnalyticsResponse(BaseModel):
    projects: ProjectAnalytics
    workers: WorkerAnalytics
    resources: ResourceAnalytics
    inventory: InventoryAnalytics
    procurements: ProcurementAnalytics


class ResourceUtilization(BaseModel):
    resource_id: int
    resource_name: str
    available: int
    allocated: int
    utilization: float