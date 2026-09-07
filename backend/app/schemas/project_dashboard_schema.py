from pydantic import BaseModel


class ProjectBudgetDashboard(BaseModel):
    total_budget: float
    total_actual_cost: float
    remaining_budget: float
    utilization_percentage: float


class ProjectWorkforceDashboard(BaseModel):
    total_workers: int
    active_allocations: int
    present: int
    absent: int


class ProjectResourceDashboard(BaseModel):
    total_quantity: int
    allocated_quantity: int
    available_quantity: int
    utilization: float


class ProjectProcurementDashboard(BaseModel):
    total_procurements: int
    pending_procurements: int
    completed_procurements: int


class ProjectDashboardResponse(BaseModel):
    project_id: int
    project_name: str
    project_code: str | None
    project_category: str | None
    status: str | None
    progress: float

    budget: ProjectBudgetDashboard
    workforce: ProjectWorkforceDashboard
    resources: ProjectResourceDashboard
    procurement: ProjectProcurementDashboard
