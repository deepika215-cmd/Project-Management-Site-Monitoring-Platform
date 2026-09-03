from pydantic import BaseModel


class ProjectAnalytics(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    pending_projects: int


class WorkerAnalytics(BaseModel):
    total_workers: int
    present_workers: int
    absent_workers: int


class ResourceAnalytics(BaseModel):
    total_resources: int


class InventoryAnalytics(BaseModel):
    total_inventory: int


class ProcurementAnalytics(BaseModel):
    total_procurements: int


class SummaryAnalytics(BaseModel):
    total_projects: int
    total_workers: int
    total_resources: int
    total_inventory: int
    total_procurements: int
    total_notifications: int