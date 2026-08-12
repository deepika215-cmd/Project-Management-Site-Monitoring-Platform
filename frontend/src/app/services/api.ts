import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class Api {

  private readonly baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  // =====================================================
  // AUTHENTICATION
  // =====================================================

  // Login
  login(email: string, password: string) {


    const body = new URLSearchParams();

    body.set('username', email);
    body.set('password', password);

    return this.http.post<any>(
      `${this.baseUrl}/auth/login`,
      body.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );


  }

  // Register
  register(user: any) {


    return this.http.post<any>(
      `${this.baseUrl}/auth/register`,
      user
    );


  }

  // Get currently logged-in user
  getCurrentUser() {


    const token = localStorage.getItem('token');

    return this.http.get<any>(
      `${this.baseUrl}/auth/me`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
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
      { email }
    );


  }

  // Reset password using the token from the emailed/logged reset link
  resetPassword(token: string, newPassword: string) {


    return this.http.post<any>(
      `${this.baseUrl}/auth/reset-password`,
      {
        token,
        new_password: newPassword
      }
    );


  }

  // =====================================================
  // USERS
  // =====================================================

  // Get all users
  getUsers() {
    const token = localStorage.getItem('token');

    return this.http.get<any[]>(
      `${this.baseUrl}/users/`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }

  // Get single user
  getUser(userId: number) {
    const token = localStorage.getItem('token');

    return this.http.get<any>(
      `${this.baseUrl}/users/${userId}`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }

  // Create user
  createUser(user: any) {
    const token = localStorage.getItem('token');

    return this.http.post<any>(
      `${this.baseUrl}/users/`,
      user,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }

  // Update user
  updateUser(userId: number, user: any) {
    const token = localStorage.getItem('token');

    return this.http.put<any>(
      `${this.baseUrl}/users/${userId}`,
      user,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }

  // Delete user
  deleteUser(userId: number) {
    const token = localStorage.getItem('token');

    return this.http.delete<any>(
      `${this.baseUrl}/users/${userId}`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );
  }

  // =====================================================
  // PROJECTS
  // =====================================================

  // Get all projects
  getProjects() {


    return this.http.get<any[]>(
      `${this.baseUrl}/projects/`
    );


  }

  // Get project by ID
  getProject(projectId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/projects/${projectId}`
    );


  }

  // Create project
  createProject(project: any) {


    return this.http.post<any>(
      `${this.baseUrl}/projects/`,
      project
    );


  }

  // Update project
  updateProject(projectId: number, project: any) {


    return this.http.put<any>(
      `${this.baseUrl}/projects/${projectId}`,
      project
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

  // =====================================================
  // MILESTONES
  // =====================================================

  // Get milestones
  getMilestones() {


    return this.http.get<any[]>(
      `${this.baseUrl}/milestones/`
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


    return this.http.get<any>(
      `${this.baseUrl}/milestones/${milestoneId}`
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


    return this.http.get<any[]>(
      `${this.baseUrl}/resources/`
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


    return this.http.get<any[]>(
      `${this.baseUrl}/workers/`
    );


  }

  createWorker(worker: any) {


    return this.http.post<any>(
      `${this.baseUrl}/workers/`,
      worker
    );


  }

  getWorker(workerId: number) {


    return this.http.get<any>(
      `${this.baseUrl}/workers/${workerId}`
    );


  }

  updateWorker(workerId: number, worker: any) {


    return this.http.put<any>(
      `${this.baseUrl}/workers/${workerId}`,
      worker
    );


  }

  deleteWorker(workerId: number) {


    return this.http.delete<any>(
      `${this.baseUrl}/workers/${workerId}`
    );


  }


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

  getNotifications() {


    return this.http.get<any[]>(
      `${this.baseUrl}/notification/`
    );


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

}
