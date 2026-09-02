import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpHeaders
} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class Api {

  // =====================================================
  // BASE URL
  // =====================================================

  private readonly baseUrl = 'http://localhost:8000';


  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(
    private http: HttpClient
  ) {}


  // =====================================================
  // AUTHORIZATION HEADER
  // =====================================================

  private getAuthHeaders(): HttpHeaders {

    const token = localStorage.getItem('token');

    let headers = new HttpHeaders();

    if (token) {
      headers = headers.set(
        'Authorization',
        `Bearer ${token}`
      );
    }

    return headers;
  }


  // =====================================================
  // AUTHENTICATION
  // =====================================================

  login(
    email: string,
    password: string
  ) {

    const body = new URLSearchParams();

    body.set('username', email);
    body.set('password', password);

    return this.http.post<any>(
      `${this.baseUrl}/auth/login`,
      body.toString(),
      {
        headers: {
          'Content-Type':
            'application/x-www-form-urlencoded'
        }
      }
    );
  }


  register(user: any) {

    return this.http.post<any>(
      `${this.baseUrl}/auth/register`,
      user
    );
  }


  getCurrentUser() {

    return this.http.get<any>(
      `${this.baseUrl}/auth/me`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateProfile(profile: any) {

    return this.http.put<any>(
      `${this.baseUrl}/auth/me`,
      profile,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  changePassword(
    currentPassword: string,
    newPassword: string
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/auth/change-password`,
      {
        current_password: currentPassword,
        new_password: newPassword
      },
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  forgotPassword(email: string) {

    return this.http.post<any>(
      `${this.baseUrl}/auth/forgot-password`,
      {
        email
      }
    );
  }


  resetPassword(
    token: string,
    newPassword: string
  ) {

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

  getUsers() {

    return this.http.get<any[]>(
      `${this.baseUrl}/users/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getUser(
    userId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/users/${userId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createUser(user: any) {

    return this.http.post<any>(
      `${this.baseUrl}/users/`,
      user,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateUser(
    userId: number,
    user: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/users/${userId}`,
      user,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteUser(
    userId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/users/${userId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // PROJECTS
  // =====================================================

  getProjects() {

    return this.http.get<any[]>(
      `${this.baseUrl}/projects/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProject(
    projectId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/projects/${projectId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createProject(project: any) {

    return this.http.post<any>(
      `${this.baseUrl}/projects/`,
      project,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateProject(
    projectId: number,
    project: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/projects/${projectId}`,
      project,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteProject(
    projectId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/projects/${projectId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateProjectStatus(
    projectId: number,
    status: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/projects/${projectId}/status`,
      status,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  closeProject(
    projectId: number
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/projects/${projectId}/close`,
      {},
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProjectTracking(
    projectId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/projects/${projectId}/tracking`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // MILESTONES
  // =====================================================

  getMilestones() {

    return this.http.get<any[]>(
      `${this.baseUrl}/milestones/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createMilestone(
    milestone: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/milestones/`,
      milestone,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getMilestone(
    milestoneId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/milestones/${milestoneId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateMilestone(
    milestoneId: number,
    milestone: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/milestones/${milestoneId}`,
      milestone,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteMilestone(
    milestoneId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/milestones/${milestoneId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // RESOURCES
  // =====================================================

  getResources() {

    return this.http.get<any[]>(
      `${this.baseUrl}/resources/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createResource(
    resource: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/resources/`,
      resource,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getResource(
    resourceId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/resources/${resourceId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateResource(
    resourceId: number,
    resource: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/resources/${resourceId}`,
      resource,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteResource(
    resourceId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/resources/${resourceId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  allocateResource(
    resourceId: number,
    data: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/resources/${resourceId}/allocate`,
      data,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  releaseResource(
    resourceId: number,
    quantity: number
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/resources/${resourceId}/release`,
      {
        quantity
      },
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getResourceUtilization(
    resourceId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/resources/${resourceId}/utilization`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // INVENTORY
  // =====================================================

  getInventory() {

    return this.http.get<any[]>(
      `${this.baseUrl}/inventory/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createInventory(
    inventory: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/inventory/`,
      inventory,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getInventoryById(
    inventoryId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/inventory/${inventoryId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateInventory(
    inventoryId: number,
    inventory: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/inventory/${inventoryId}`,
      inventory,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteInventory(
    inventoryId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/inventory/${inventoryId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  useInventory(
    inventoryId: number,
    data: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/inventory/${inventoryId}/use`,
      data,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  releaseInventory(
    inventoryId: number,
    quantity: number
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/inventory/${inventoryId}/release`,
      {
        quantity
      },
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getInventoryUtilization(
    inventoryId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/inventory/${inventoryId}/utilization`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // WORKERS
  // =====================================================

  getWorkers() {

    return this.http.get<any[]>(
      `${this.baseUrl}/workers/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createWorker(
    worker: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/workers/`,
      worker,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getWorker(
    workerId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/workers/${workerId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateWorker(
    workerId: number,
    worker: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/workers/${workerId}`,
      worker,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteWorker(
    workerId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/workers/${workerId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // ATTENDANCE
  // =====================================================

  getAttendance() {

    return this.http.get<any[]>(
      `${this.baseUrl}/attendance/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createAttendance(
    attendance: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/attendance/`,
      attendance,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getAttendanceById(
    attendanceId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/attendance/${attendanceId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateAttendance(
    attendanceId: number,
    attendance: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/attendance/${attendanceId}`,
      attendance,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteAttendance(
    attendanceId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/attendance/${attendanceId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // PROCUREMENT
  // =====================================================

  getProcurements() {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createProcurement(
    procurement: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/procurement/`,
      procurement,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProcurement(
    procurementId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/${procurementId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateProcurement(
    procurementId: number,
    procurement: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/procurement/${procurementId}`,
      procurement,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteProcurement(
    procurementId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/procurement/${procurementId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // PROCUREMENT REQUESTS
  // =====================================================

  getProcurementRequests() {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/requests/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createProcurementRequest(
    payload: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/procurement/requests/`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProcurementRequest(
    id: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/requests/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateProcurementRequest(
    id: number,
    payload: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/procurement/requests/${id}`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteProcurementRequest(
    id: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/procurement/requests/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // VENDORS
  // =====================================================

  getVendors() {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/vendors/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createVendor(
    payload: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/procurement/vendors/`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getVendor(
    id: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/vendors/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateVendor(
    id: number,
    payload: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/procurement/vendors/${id}`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteVendor(
    id: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/procurement/vendors/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // VENDOR PROCUREMENT RECORDS
  // =====================================================

  getVendorProcurements(
    vendorId: number
  ) {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/vendors/${vendorId}/procurements`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // PURCHASE ORDERS
  // =====================================================

  getPurchaseOrders() {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/purchase-orders/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createPurchaseOrder(
    payload: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/procurement/purchase-orders/`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getPurchaseOrder(
    id: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/purchase-orders/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updatePurchaseOrder(
    id: number,
    payload: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/procurement/purchase-orders/${id}`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deletePurchaseOrder(
    id: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/procurement/purchase-orders/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // INVOICES
  // =====================================================

  getInvoices() {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/invoices/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createInvoice(
    payload: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/procurement/invoices/`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getInvoice(
    id: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/invoices/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateInvoice(
    id: number,
    payload: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/procurement/invoices/${id}`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteInvoice(
    id: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/procurement/invoices/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // CATEGORIES
  // =====================================================

  getCategories() {

    return this.http.get<any[]>(
      `${this.baseUrl}/procurement/categories/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createCategory(
    payload: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/procurement/categories/`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getCategory(
    id: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/categories/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateCategory(
    id: number,
    payload: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/procurement/categories/${id}`,
      payload,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteCategory(
    id: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/procurement/categories/${id}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // PROCUREMENT DASHBOARD
  // =====================================================

  getProcurementDashboardSummary() {

    return this.http.get<any>(
      `${this.baseUrl}/procurement/dashboard/summary`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // NOTIFICATIONS
  // =====================================================

  getNotifications() {

    return this.http.get<any[]>(
      `${this.baseUrl}/notification/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createNotification(
    notification: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/notification/`,
      notification,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getNotification(
    notificationId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/notification/${notificationId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateNotification(
    notificationId: number,
    notification: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/notification/${notificationId}`,
      notification,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteNotification(
    notificationId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/notification/${notificationId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // MARK NOTIFICATION AS READ
  // =====================================================

  markNotificationAsRead(
    notificationId: number
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/notification/${notificationId}/read`,
      {},
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // MARK NOTIFICATION AS UNREAD
  // =====================================================

  markNotificationAsUnread(
    notificationId: number
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/notification/${notificationId}/unread`,
      {},
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // REPORTS
  // =====================================================

  getReports() {

    return this.http.get<any[]>(
      `${this.baseUrl}/report/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  createReport(
    report: any
  ) {

    return this.http.post<any>(
      `${this.baseUrl}/report/`,
      report,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getReport(
    reportId: number
  ) {

    return this.http.get<any>(
      `${this.baseUrl}/report/${reportId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  updateReport(
    reportId: number,
    report: any
  ) {

    return this.http.put<any>(
      `${this.baseUrl}/report/${reportId}`,
      report,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  deleteReport(
    reportId: number
  ) {

    return this.http.delete<any>(
      `${this.baseUrl}/report/${reportId}`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  // =====================================================
  // ANALYTICS
  // =====================================================

  getAnalytics() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProjectProgress() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/project-progress`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getResourceUtilizationAnalytics() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/resource-utilization`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getInventoryStatus() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/inventory-status`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProcurementStatus() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/procurement-status`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getWorkerAttendance() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/worker-attendance`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getProjectSummary() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/project-summary`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }


  getReportSummary() {

    return this.http.get<any>(
      `${this.baseUrl}/analytics/report-summary`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }

}