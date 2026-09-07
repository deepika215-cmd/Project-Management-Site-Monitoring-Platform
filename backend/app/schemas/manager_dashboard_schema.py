from pydantic import BaseModel


class WorkforceDashboard(BaseModel):
    total_workers: int
    active_allocations: int
    present: int
    absent: int


class ResourceDashboard(BaseModel):
    total_quantity: int
    allocated_quantity: int
    available_quantity: int
    utilization: float


class ProjectProgressDashboard(BaseModel):
    project_id: int
    project_name: str
    progress: float


class BudgetDashboard(BaseModel):
    total_budget: float
    total_actual_cost: float
    remaining_budget: float
    utilization_percentage: float


class ProcurementDashboard(BaseModel):
    total_procurements: int
    pending_procurements: int
    completed_procurements: int


class ManagerDashboardResponse(BaseModel):
    project_progress: list[ProjectProgressDashboard]
    budget: BudgetDashboard
    workforce: WorkforceDashboard
    resources: ResourceDashboard
    procurement: ProcurementDashboard
