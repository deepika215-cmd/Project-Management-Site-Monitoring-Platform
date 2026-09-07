import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class Api {

  private readonly baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  /** Normalize backend objects once so every page can safely use either the
   * original FastAPI snake_case names or the older frontend aliases. This
   * removes blank dropdown/table values caused by inconsistent property names.
   */
  private normalizeProject(project: any): any {
    const p = project || {};
    const name = p.project_name ?? p.name ?? '';
    const code = p.project_code ?? p.code ?? (p.id ? `BT-${String(p.id).padStart(3, '0')}` : '');
    const start = p.start_date ?? p.startDate ?? '';
    const end = p.end_date ?? p.completionDate ?? p.endDate ?? '';
    const managerId = p.manager_id ?? p.managerId ?? null;
    const category = p.project_category ?? p.category ?? 'Residential';
    const priority = p.priority ?? p.project_priority ?? 'Medium';
    const managerName = p.manager_name ?? p.project_manager_name ?? p.managerName ?? '';
    return { ...p, project_name: name, name, project_code: code, code, start_date: start, startDate: start, end_date: end, endDate: end, completionDate: end, manager_id: managerId, managerId, project_category: category, category, priority, project_priority: priority, manager_name: managerName, managerName };
  }

  private normalizeUser(user: any): any {
    const u = user || {};
    const name = u.name ?? u.full_name ?? u.fullName ?? '';
    return { ...u, name, full_name: name, fullName: name, is_active: u.is_active ?? u.isActive ?? true, isActive: u.is_active ?? u.isActive ?? true };
  }

  private normalizeMilestone(milestone: any): any {
    const m = milestone || {};
    const title = m.title ?? m.name ?? m.milestone_name ?? '';
    return { ...m, title, name: title, milestone_name: title, project_id: m.project_id ?? m.projectId, projectId: m.project_id ?? m.projectId };
  }

  private normalizeResource(resource: any): any {
    const r = resource || {};
    const name = r.name ?? r.resource_name ?? '';
    const type = r.type ?? r.category ?? 'Equipment';
    const projectId = r.project_id ?? r.projectId ?? null;
    const allocated = r.allocated_quantity ?? r.allocatedQuantity ?? 0;
    return { ...r, name, resource_name: name, type, category: type, project_id: projectId, projectId, allocated_quantity: allocated, allocatedQuantity: allocated };
  }

  private normalizeWorker(worker: any): any {
    const w = worker || {};
    const name = w.name ?? w.worker_name ?? w.full_name ?? '';
    return { ...w, name, worker_name: name, full_name: name, contractor_id: w.contractor_id ?? w.contractorId ?? null, contractorId: w.contractor_id ?? w.contractorId ?? null };
  }

  private normalizeContractor(contractor: any): any {
    const c = contractor || {};
    const name = c.name ?? c.contractor_name ?? c.company_name ?? '';
    return { ...c, name, contractor_name: name, company_name: c.company_name ?? c.companyName ?? '', project_id: c.project_id ?? c.projectId ?? null, projectId: c.project_id ?? c.projectId ?? null };
  }

  private normalizeWorkerAssignment(assignment: any): any {
    const a = assignment || {};
    const activity = a.work_activity ?? a.activity ?? '';
    const start = a.assignment_start_date ?? a.start_date ?? '';
    const end = a.assignment_end_date ?? a.end_date ?? null;
    const status = a.assignment_status ?? a.status ?? 'ACTIVE';
    return { ...a, activity, work_activity: activity, start_date: start, assignment_start_date: start, end_date: end, assignment_end_date: end, status, assignment_status: status };
  }

  private normalizePayroll(payroll: any): any {
    const p = payroll || {};
    const status = p.payroll_status ?? p.status ?? 'PENDING';
    return { ...p, status, payroll_status: status, estimated_pay: Number(p.estimated_pay ?? 0) };
  }

  // =====================================================
  // AUTHENTICATION
  // =====================================================

  // Login - JSON endpoint used by the Angular app.
  // The backend also keeps /auth/login for Swagger/OAuth2 form login.
  login(email: string, password: string) {
    return this.http.post<any>(
      `${this.baseUrl}/auth/login-json`,
      { email: email.trim(), password }
    );
  }

  // Register
  register(user: any) {
    const payload = {
      ...user,
      name: String(user?.name || '').trim(),
      email: String(user?.email || '').trim().toLowerCase(),
      phone: String(user?.phone || '').trim(),
      role: String(user?.role || '').trim().toUpperCase(),
      employee_id: user?.employee_id ? String(user.employee_id).trim() : null,
      department: user?.department ? String(user.department).trim() : null,
      address: user?.address ? String(user.address).trim() : null
    };

    return this.http.post<any>(
      `${this.baseUrl}/auth/register`,
      payload
    );
  }

  // Get currently logged-in user
  getCurrentUser() {
    const token = localStorage.getItem('token');

    return this.http.get<any>(
      `${this.baseUrl}/auth/me`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token || ''}`
        })
      }
    ).pipe(
      map(item => this.normalizeUser(item))
    );
  }

  // Update my profile (name / phone / email)
  updateProfile(profile: any) {


    const token = localStorage.getItem('token');
    return this.http.put<any>(
      `${this.baseUrl}/auth/me`,
      profile,
      { headers: new HttpHeaders({ Authorization: `Bearer ${token}` }) }
    );


  }

  // Change my password
  changePassword(currentPassword: string, newPassword: string) {


    const token = localStorage.getItem('token');
    return this.http.put<any>(
      `${this.baseUrl}/auth/change-password`,
      {
        current_password: currentPassword,
        new_password: newPassword
      },
      { headers: new HttpHeaders({ Authorization: `Bearer ${token}` }) }
    );


  }

  // Request a password reset link
  forgotPassword(email: string) {
    return this.http.post<any>(
      `${this.baseUrl}/auth/forgot-password`,
      { email: String(email || '').trim().toLowerCase() }
    );
  }

  // Reset password using the token from the emailed/logged reset link
  resetPassword(token: string, newPassword: string) {
    return this.http.post<any>(
      `${this.baseUrl}/auth/reset-password`,
      {
        token: String(token || '').trim(),
        new_password: newPassword
      }
    );
  }

  // =====================================================
  // USERS
  // =====================================================

  // Get all users
  getUsers() {
    return this.http.get<any[]>(`${this.baseUrl}/users/`).pipe(
      map(items => (items || []).map(item => this.normalizeUser(item)))
    );
  }

  // Get single user
  getUser(userId: number) {
    return this.http.get<any>(`${this.baseUrl}/users/${userId}`).pipe(
      map(item => this.normalizeUser(item))
    );
  }

  // Create user
  createUser(user: any) {


    return this.http.post<any>(
      `${this.baseUrl}/users/`,
      user
    );


  }

  // Update user
  updateUser(userId: number, user: any) {


    return this.http.put<any>(
      `${this.baseUrl}/users/${userId}`,
      user
    );


  }

  // Delete user
  deleteUser(userId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/users/${userId}`
    );


  }

  // =====================================================
  // PROJECTS
  // =====================================================

  // Get all projects
  getProjects() {
    return this.http.get<any[]>(`${this.baseUrl}/projects/`).pipe(
      map(items => (items || []).map(item => this.normalizeProject(item)))
    );
  }

  // Get project by ID
  getProject(projectId: number) {
    return this.http.get<any>(`${this.baseUrl}/projects/${projectId}`).pipe(
      map(item => this.normalizeProject(item))
    );
  }

  // Create project
  createProject(project: any) {
    return this.http.post<any>(`${this.baseUrl}/projects/`, project).pipe(
      map(item => this.normalizeProject(item))
    );
  }

  // Update project
  updateProject(projectId: number, project: any) {
    return this.http.put<any>(`${this.baseUrl}/projects/${projectId}`, project).pipe(
      map(item => this.normalizeProject(item))
    );
  }

  // Delete project
  deleteProject(projectId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/projects/${projectId}`
    );


  }

  // Update project status
  updateProjectStatus(projectId: number, status: any) {


    return this.http.put<any>(
      `${this.baseUrl}/projects/${projectId}/status`,
      status
    );


  }

  // Close project
  closeProject(projectId: number) {


    return this.http.put<any>(
      `${this.baseUrl}/projects/${projectId}/close`,
      {}
    );


  }

  // Project tracking
  getProjectTracking(projectId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/projects/${projectId}/tracking`
    );


  }

  // Project managers available for project assignment
  getAvailableProjectManagers() {
    return this.http.get<any[]>(`${this.baseUrl}/projects/available-managers`).pipe(
      map(items => (items || []).map(item => this.normalizeUser(item)))
    );
  }

  // =====================================================
  // MILESTONES
  // =====================================================

  // Get milestones
  getMilestones() {
    return this.http.get<any[]>(`${this.baseUrl}/milestones/`).pipe(
      map(items => (items || []).map(item => this.normalizeMilestone(item)))
    );
  }

  // Create milestone
  createMilestone(milestone: any) {


    return this.http.post<any>(
      `${this.baseUrl}/milestones/`,
      milestone
    );


  }

  // Get milestone
  getMilestone(milestoneId: number) {
    return this.http.get<any>(`${this.baseUrl}/milestones/${milestoneId}`).pipe(
      map(item => this.normalizeMilestone(item))
    );
  }

  // Update milestone
  updateMilestone(milestoneId: number, milestone: any) {


    return this.http.put<any>(
      `${this.baseUrl}/milestones/${milestoneId}`,
      milestone
    );


  }

  // Delete milestone
  deleteMilestone(milestoneId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/milestones/${milestoneId}`
    );


  }

  // =====================================================
  // RESOURCES
  // =====================================================

  // Get resources
  getResources() {
    return this.http.get<any[]>(`${this.baseUrl}/resources/`).pipe(
      map(items => (items || []).map(item => this.normalizeResource(item)))
    );
  }

  // Create resource
  createResource(resource: any) {


    return this.http.post<any>(
      `${this.baseUrl}/resources/`,
      resource
    );


  }

  // Get resource
  getResource(resourceId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/resources/${resourceId}`
    );


  }

  // Update resource
  updateResource(resourceId: number, resource: any) {


    return this.http.put<any>(
      `${this.baseUrl}/resources/${resourceId}`,
      resource
    );


  }

  // Delete resource
  deleteResource(resourceId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/resources/${resourceId}`
    );


  }

  // Allocate resource
  allocateResource(resourceId: number, data: any) {


    return this.http.put<any>(
      `${this.baseUrl}/resources/${resourceId}/allocate`,
      data
    );


  }

  // Release resource
  releaseResource(resourceId: number, quantity: number) {
    return this.http.put<any>(
      `${this.baseUrl}/resources/${resourceId}/release`,
      { quantity }
    );
  }

  // Resource utilization
  getResourceUtilization(resourceId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/resources/${resourceId}/utilization`
    );


  }

  // =====================================================
  // INVENTORY
  // =====================================================

  getInventory() {


    return this.http.get<any[]>(
      `${this.baseUrl}/inventory/`
    );


  }

  createInventory(inventory: any) {


    return this.http.post<any>(
      `${this.baseUrl}/inventory/`,
      inventory
    );


  }

  getInventoryById(inventoryId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/inventory/${inventoryId}`
    );


  }

  updateInventory(inventoryId: number, inventory: any) {


    return this.http.put<any>(
      `${this.baseUrl}/inventory/${inventoryId}`,
      inventory
    );


  }

  deleteInventory(inventoryId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/inventory/${inventoryId}`
    );


  }

  useInventory(inventoryId: number, data: any) {


    return this.http.put<any>(
      `${this.baseUrl}/inventory/${inventoryId}/use`,
      data
    );


  }

  releaseInventory(inventoryId: number, quantity: number) {
    return this.http.put<any>(
      `${this.baseUrl}/inventory/${inventoryId}/release`,
      { quantity }
    );
  }

  getInventoryUtilization(inventoryId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/inventory/${inventoryId}/utilization`
    );


  }

  // =====================================================
  // WORKERS
  // =====================================================

  getWorkers() {
    return this.http.get<any[]>(`${this.baseUrl}/workers/`).pipe(
      map(items => (items || []).map(item => this.normalizeWorker(item)))
    );
  }

  createWorker(worker: any) {
    return this.http.post<any>(`${this.baseUrl}/workers/`, worker).pipe(
      map(item => this.normalizeWorker(item))
    );
  }

  bulkCreateWorkers(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<any>(`${this.baseUrl}/workers/bulk`, formData).pipe(
      map(result => ({
        ...result,
        created_workers: (result?.created_workers || []).map((item: any) => this.normalizeWorker(item))
      }))
    );
  }

  getWorkerBulkTemplate() {
    return this.http.get<any>(`${this.baseUrl}/workers/bulk-template`);
  }

  getWorker(workerId: number) {
    return this.http.get<any>(`${this.baseUrl}/workers/${workerId}`).pipe(
      map(item => this.normalizeWorker(item))
    );
  }

  updateWorker(workerId: number, worker: any) {
    return this.http.put<any>(`${this.baseUrl}/workers/${workerId}`, worker).pipe(
      map(item => this.normalizeWorker(item))
    );
  }

  deleteWorker(workerId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/workers/${workerId}`
    );


  }

  // =====================================================
  // CONTRACTORS
  // =====================================================

  getContractors() {
    return this.http.get<any[]>(`${this.baseUrl}/contractors/`).pipe(
      map(items => (items || []).map(item => this.normalizeContractor(item)))
    );
  }

  createContractor(contractor: any) {
    return this.http.post<any>(`${this.baseUrl}/contractors/`, contractor).pipe(
      map(item => this.normalizeContractor(item))
    );
  }

  updateContractor(contractorId: number, contractor: any) {
    return this.http.put<any>(`${this.baseUrl}/contractors/${contractorId}`, contractor).pipe(
      map(item => this.normalizeContractor(item))
    );
  }

  deleteContractor(contractorId: number) {
    return this.http.delete<any>(`${this.baseUrl}/contractors/${contractorId}`);
  }

  assignContractorToProject(contractorId: number, projectId: number) {
    return this.http.put<any>(`${this.baseUrl}/contractors/${contractorId}/project/${projectId}`, {}).pipe(
      map(item => this.normalizeContractor(item))
    );
  }

  getWorkforceCategories() { return this.http.get<any[]>(`${this.baseUrl}/workforce-categories/`); }
  createWorkforceCategory(data: any) { return this.http.post<any>(`${this.baseUrl}/workforce-categories/`, data); }


  // =====================================================
  // ATTENDANCE
  // =====================================================

  getAttendance() {


    return this.http.get<any[]>(
      `${this.baseUrl}/attendance/`
    );


  }

  createAttendance(attendance: any) {


    return this.http.post<any>(
      `${this.baseUrl}/attendance/`,
      attendance
    );


  }

  getAttendanceById(attendanceId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/attendance/${attendanceId}`
    );


  }

  updateAttendance(attendanceId: number, attendance: any) {


    return this.http.put<any>(
      `${this.baseUrl}/attendance/${attendanceId}`,
      attendance
    );


  }

  deleteAttendance(attendanceId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/attendance/${attendanceId}`
    );


  }


  // =====================================================
  // PROCUREMENT
  // =====================================================

  getProcurements() {


    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/`
    );


  }

  createProcurement(procurement: any) {


    return this.http.post<any>(
      `${this.baseUrl}/procurement/`,
      procurement
    );


  }

  getProcurement(procurementId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/procurement/${procurementId}`
    );


  }

  updateProcurement(procurementId: number, procurement: any) {


    return this.http.put<any>(
      `${this.baseUrl}/procurement/${procurementId}`,
      procurement
    );


  }

  deleteProcurement(procurementId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/procurement/${procurementId}`
    );


  }


  // =====================================================
  // NOTIFICATIONS
  // =====================================================

  // Current user's notifications. This is safe for every dashboard role.
  getNotifications() {
    return this.http.get<any[]>(`${this.baseUrl}/notification/my`);
  }

  getMyNotifications() {
    return this.http.get<any[]>(`${this.baseUrl}/notification/my`);
  }

  // Admin / Project Manager full notification feed.
  getAllNotifications() {
    return this.http.get<any[]>(`${this.baseUrl}/notification/`);
  }

  getUnreadNotificationCount() {
    return this.http.get<any>(`${this.baseUrl}/notification/my/unread/count`);
  }

  markAllMyNotificationsRead() {
    return this.http.put<any>(`${this.baseUrl}/notification/my/read-all`, {});
  }

  createNotification(notification: any) {


    return this.http.post<any>(
      `${this.baseUrl}/notification/`,
      notification
    );


  }

  getNotification(notificationId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/notification/${notificationId}`
    );


  }

  updateNotification(notificationId: number, notification: any) {


    return this.http.put<any>(
      `${this.baseUrl}/notification/${notificationId}`,
      notification
    );


  }

  deleteNotification(notificationId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/notification/${notificationId}`
    );


  }

  // =====================================================
  // REPORTS
  // =====================================================

  getReports() {


    return this.http.get<any[]>(
      `${this.baseUrl}/report/`
    );


  }

  createReport(report: any) {


    return this.http.post<any>(
      `${this.baseUrl}/report/`,
      report
    );


  }

  getReport(reportId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/report/${reportId}`
    );


  }

  updateReport(reportId: number, report: any) {


    return this.http.put<any>(
      `${this.baseUrl}/report/${reportId}`,
      report
    );


  }

  deleteReport(reportId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/report/${reportId}`
    );


  }

  // =====================================================
  // ANALYTICS
  // =====

  getAnalytics() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/`
    );


  }

  getProjectProgress() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/project-progress`
    );


  }

  getResourceUtilizationAnalytics() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/resource-utilization`
    );


  }

  getInventoryStatus() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/inventory-status`
    );


  }

  getProcurementStatus() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/procurement-status`
    );


  }

  getWorkerAttendance() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/worker-attendance`
    );


  }

  getProjectSummary() {


    return this.http.get<any>(
      `${this.baseUrl}/analytics/project-summary`
    );


  }

  getReportSummary() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/report-summary`
    );


  }


  // =====================================================
  // MODULE 3 - SITE PROGRESS
  // =====================================================
  getDailyProgress() { return this.http.get<any[]>(`${this.baseUrl}/daily-progress/`); }
  createDailyProgress(data: any) { return this.http.post<any>(`${this.baseUrl}/daily-progress/`, data); }
  updateDailyProgress(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/daily-progress/${id}`, data); }
  deleteDailyProgress(id: number) { return this.http.delete<any>(`${this.baseUrl}/daily-progress/${id}`); }
  getWeeklyProgress() { return this.http.get<any[]>(`${this.baseUrl}/weekly-progress/`); }
  createWeeklyProgress(data: any) { return this.http.post<any>(`${this.baseUrl}/weekly-progress/`, data); }
  deleteWeeklyProgress(id: number) { return this.http.delete<any>(`${this.baseUrl}/weekly-progress/${id}`); }
  getDelayRecords() { return this.http.get<any[]>(`${this.baseUrl}/delay-records/`); }
  createDelayRecord(data: any) { return this.http.post<any>(`${this.baseUrl}/delay-records/`, data); }
  deleteDelayRecord(id: number) { return this.http.delete<any>(`${this.baseUrl}/delay-records/${id}`); }
  getProgressPhotos() { return this.http.get<any[]>(`${this.baseUrl}/progress-photos/`); }

  // =====================================================
  // MODULE 4 - MACHINERY & MAINTENANCE
  // =====================================================
  getMachinery() { return this.http.get<any[]>(`${this.baseUrl}/machinery/`); }
  createMachinery(data: any) { return this.http.post<any>(`${this.baseUrl}/machinery/`, data); }
  updateMachinery(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/machinery/${id}`, data); }
  updateMachineryStatus(id: number, status: string) { return this.http.put<any>(`${this.baseUrl}/machinery/${id}/status`, { status }); }
  addMachineryHours(id: number, hours: number) { return this.http.put<any>(`${this.baseUrl}/machinery/${id}/hours`, { hours }); }
  deleteMachinery(id: number) { return this.http.delete<any>(`${this.baseUrl}/machinery/${id}`); }
  getMaintenance() { return this.http.get<any[]>(`${this.baseUrl}/maintenance/`); }
  getUpcomingMaintenance() { return this.http.get<any[]>(`${this.baseUrl}/maintenance/upcoming`); }
  createMaintenance(data: any) { return this.http.post<any>(`${this.baseUrl}/maintenance/`, data); }
  updateMaintenance(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/maintenance/${id}`, data); }
  updateMaintenanceStatus(id: number, status: string) { return this.http.put<any>(`${this.baseUrl}/maintenance/${id}/status`, { status }); }
  completeMaintenance(id: number, completionDate: string) { return this.http.put<any>(`${this.baseUrl}/maintenance/${id}/complete`, { completion_date: completionDate }); }
  deleteMaintenance(id: number) { return this.http.delete<any>(`${this.baseUrl}/maintenance/${id}`); }

  // =====================================================
  // MODULE 5 - MATERIAL LIFECYCLE
  // =====================================================
  getMaterials() { return this.http.get<any[]>(`${this.baseUrl}/materials/`); }
  createMaterial(data: any) { return this.http.post<any>(`${this.baseUrl}/materials/`, data); }
  getMaterialRequests() { return this.http.get<any[]>(`${this.baseUrl}/material-requests/`); }
  createMaterialRequest(data: any) { return this.http.post<any>(`${this.baseUrl}/material-requests/`, data); }
  approveMaterialRequest(id: number) { return this.http.put<any>(`${this.baseUrl}/material-requests/${id}/approve`, {}); }
  rejectMaterialRequest(id: number) { return this.http.put<any>(`${this.baseUrl}/material-requests/${id}/reject`, {}); }
  fulfillMaterialRequest(id: number) { return this.http.put<any>(`${this.baseUrl}/material-requests/${id}/fulfill`, {}); }
  getMaterialAllocations() { return this.http.get<any[]>(`${this.baseUrl}/material-allocations/`); }
  createMaterialAllocation(data: any) { return this.http.post<any>(`${this.baseUrl}/material-allocations/`, data); }
  consumeMaterialAllocation(id: number) { return this.http.post<any>(`${this.baseUrl}/material-allocations/${id}/consume`, {}); }
  getStockMovements() { return this.http.get<any[]>(`${this.baseUrl}/stock-movements/`); }
  createStockMovement(data: any) { return this.http.post<any>(`${this.baseUrl}/stock-movements/`, data); }

  // =====================================================
  // MODULE 7 - PROCUREMENT WORKFLOW
  // =====================================================
  getVendors() { return this.http.get<any[]>(`${this.baseUrl}/vendors/`); }
  createVendor(data: any) { return this.http.post<any>(`${this.baseUrl}/vendors/`, data); }
  updateVendor(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/vendors/${id}`, data); }
  deleteVendor(id: number) { return this.http.delete<any>(`${this.baseUrl}/vendors/${id}`); }
  getProcurementRequests() { return this.http.get<any[]>(`${this.baseUrl}/procurement-requests/`); }
  createProcurementRequest(data: any) { return this.http.post<any>(`${this.baseUrl}/procurement-requests/`, data); }
  approveProcurementRequest(id: number) { return this.http.put<any>(`${this.baseUrl}/procurement-requests/${id}/approve`, {}); }
  rejectProcurementRequest(id: number) { return this.http.put<any>(`${this.baseUrl}/procurement-requests/${id}/reject`, {}); }
  getPurchaseOrders() { return this.http.get<any[]>(`${this.baseUrl}/purchase-orders/`); }
  createPurchaseOrder(data: any) { return this.http.post<any>(`${this.baseUrl}/purchase-orders/`, data); }
  completePurchaseOrder(id: number) { return this.http.put<any>(`${this.baseUrl}/purchase-orders/${id}/complete`, {}); }
  receivePurchaseOrder(id: number) { return this.http.put<any>(`${this.baseUrl}/purchase-orders/${id}/receive`, {}); }
  getInvoices() { return this.http.get<any[]>(`${this.baseUrl}/invoices/`); }
  createInvoice(data: any) { return this.http.post<any>(`${this.baseUrl}/invoices/`, data); }
  updateInvoiceStatus(id: number, status: string) { return this.http.put<any>(`${this.baseUrl}/invoices/${id}/status/${encodeURIComponent(status)}`, {}); }
  updateInvoicePaymentStatus(id: number, status: string) { return this.http.put<any>(`${this.baseUrl}/invoices/${id}/payment-status/${encodeURIComponent(status)}`, {}); }

  getInventoryLifecycleStatus() { return this.http.get<any[]>(`${this.baseUrl}/inventory/status`); }

  // =====================================================
  // WORKFORCE OPERATIONS - ASSIGNMENTS, SHIFTS, PAYROLL
  // =====================================================
  getWorkerAssignments() { return this.http.get<any[]>(`${this.baseUrl}/worker-assignments/`).pipe(map(items => (items || []).map(item => this.normalizeWorkerAssignment(item)))); }
  createWorkerAssignment(data: any) { return this.http.post<any>(`${this.baseUrl}/worker-assignments/`, data).pipe(map(item => this.normalizeWorkerAssignment(item))); }
  updateWorkerAssignment(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/worker-assignments/${id}`, data).pipe(map(item => this.normalizeWorkerAssignment(item))); }
  deleteWorkerAssignment(id: number) { return this.http.delete<any>(`${this.baseUrl}/worker-assignments/${id}`); }
  getShifts() { return this.http.get<any[]>(`${this.baseUrl}/shifts/`); }
  createShift(data: any) { return this.http.post<any>(`${this.baseUrl}/shifts/`, data); }
  updateShift(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/shifts/${id}`, data); }
  deleteShift(id: number) { return this.http.delete<any>(`${this.baseUrl}/shifts/${id}`); }
  getPayroll() { return this.http.get<any[]>(`${this.baseUrl}/payroll/`).pipe(map(items => (items || []).map(item => this.normalizePayroll(item)))); }
  createPayroll(data: any) { return this.http.post<any>(`${this.baseUrl}/payroll/`, data).pipe(map(item => this.normalizePayroll(item))); }
  updatePayroll(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/payroll/${id}`, data).pipe(map(item => this.normalizePayroll(item))); }
  deletePayroll(id: number) { return this.http.delete<any>(`${this.baseUrl}/payroll/${id}`); }

  // Site activity logs
  getSiteActivityLogs() { return this.http.get<any[]>(`${this.baseUrl}/site-activity-logs/`); }
  createSiteActivityLog(data: any) { return this.http.post<any>(`${this.baseUrl}/site-activity-logs/`, data); }
  deleteSiteActivityLog(id: number) { return this.http.delete<any>(`${this.baseUrl}/site-activity-logs/${id}`); }

  // Purchase order items
  getPurchaseOrderItems() { return this.http.get<any[]>(`${this.baseUrl}/purchase-order-items/`); }
  getPurchaseOrderItemsForOrder(id: number) { return this.http.get<any[]>(`${this.baseUrl}/purchase-order-items/order/${id}`); }
  createPurchaseOrderItem(data: any) { return this.http.post<any>(`${this.baseUrl}/purchase-order-items/`, data); }
  deletePurchaseOrderItem(id: number) { return this.http.delete<any>(`${this.baseUrl}/purchase-order-items/${id}`); }

  // Generated reports / exports
  previewReport(id: number) { return this.http.get<any>(`${this.baseUrl}/report/${id}/preview`); }
  exportReport(id: number, format: 'pdf'|'xlsx') { return this.http.get(`${this.baseUrl}/report/${id}/export?format=${format}`, { responseType: 'blob' }); }

  // Document management
  getDocuments(projectId?: number) { const q = projectId ? `?project_id=${projectId}` : ''; return this.http.get<any[]>(`${this.baseUrl}/documents/${q}`); }
  uploadDocument(projectId: number, title: string, documentType: string, file: File) { const fd = new FormData(); fd.append('project_id', String(projectId)); fd.append('title', title); fd.append('document_type', documentType); fd.append('file', file); return this.http.post<any>(`${this.baseUrl}/documents/`, fd); }
  downloadDocument(id: number) { return this.http.get(`${this.baseUrl}/documents/${id}/download`, { responseType: 'blob' }); }
  deleteDocument(id: number) { return this.http.delete<any>(`${this.baseUrl}/documents/${id}`); }

  // Notification lifecycle
  markNotificationRead(id: number) { return this.http.put<any>(`${this.baseUrl}/notification/${id}/read`, {}); }
  generateSystemAlerts() { return this.http.post<any>(`${this.baseUrl}/notification/generate-system-alerts`, {}); }
  // =====================================================
  // PROJECT SCHEDULING
  // =====================================================
  getProjectSchedule(projectId: number) { return this.http.get<any[]>(`${this.baseUrl}/project-schedules/?project_id=${projectId}`); }
  createProjectScheduleActivity(data: any) { return this.http.post<any>(`${this.baseUrl}/project-schedules/`, data); }
  updateProjectScheduleActivity(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/project-schedules/${id}`, data); }
  deleteProjectScheduleActivity(id: number) { return this.http.delete<any>(`${this.baseUrl}/project-schedules/${id}`); }

  // =====================================================
  // MODULE 11 - BUDGET & COST MANAGEMENT
  // Frontend contract for the Module 11 backend.
  // =====================================================
  getBudgetPlan(projectId: number) { return this.http.get<any>(`${this.baseUrl}/budgets/project/${projectId}`); }
  createBudgetPlan(data: any) { return this.http.post<any>(`${this.baseUrl}/budgets/`, data); }
  updateBudgetPlan(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/budgets/${id}`, data); }
  getBudgetSummary(projectId: number) { return this.http.get<any>(`${this.baseUrl}/budgets/project/${projectId}/summary`); }

  getCostEstimates(projectId: number) { return this.http.get<any[]>(`${this.baseUrl}/cost-estimates/?project_id=${projectId}`); }
  createCostEstimate(data: any) { return this.http.post<any>(`${this.baseUrl}/cost-estimates/`, data); }
  updateCostEstimate(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/cost-estimates/${id}`, data); }
  deleteCostEstimate(id: number) { return this.http.delete<any>(`${this.baseUrl}/cost-estimates/${id}`); }

  getExpenses(projectId: number) { return this.http.get<any[]>(`${this.baseUrl}/expenses/?project_id=${projectId}`); }
  createExpense(data: any) { return this.http.post<any>(`${this.baseUrl}/expenses/`, data); }
  updateExpense(id: number, data: any) { return this.http.put<any>(`${this.baseUrl}/expenses/${id}`, data); }
  deleteExpense(id: number) { return this.http.delete<any>(`${this.baseUrl}/expenses/${id}`); }

}

