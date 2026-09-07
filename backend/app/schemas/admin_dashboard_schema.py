from pydantic import BaseModel


class AdminUserSummary(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    admins: int
    managers: int
    engineers: int
    clients: int


class AdminProjectSummary(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    pending_projects: int


class AdminReportSummary(BaseModel):
    total_reports: int
    completed_reports: int
    pending_reports: int


class AdminSystemAnalytics(BaseModel):
    total_workers: int
    total_resources: int
    total_inventory_items: int
    total_procurements: int
    total_milestones: int


class AdminDashboardResponse(BaseModel):
    users: AdminUserSummary
    projects: AdminProjectSummary
    reports: AdminReportSummary
    system: AdminSystemAnalytics
