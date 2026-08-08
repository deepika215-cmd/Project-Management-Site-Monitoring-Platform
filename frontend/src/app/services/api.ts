import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
providedIn: 'root'
})
export class Api {

private baseUrl = 'http://127.0.0.1:8000';

constructor(private http: HttpClient) {}

// =====================================================
// AUTHENTICATION
// =====================================================

// Login
login(email: string, password: string) {


const body = new URLSearchParams();

body.set('username', email);
body.set('password', password);

return this.http.post(
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


return this.http.post(
  `${this.baseUrl}/auth/register`,
  user
);


}

// Get currently logged-in user
getCurrentUser() {


const token = localStorage.getItem('token');

return this.http.get(
  `${this.baseUrl}/auth/me`,
  {
    headers: new HttpHeaders({
      Authorization: `Bearer ${token}`
    })
  }
);


}

// =====================================================
// USERS
// =====================================================

// Get all users
getUsers() {


return this.http.get(
  `${this.baseUrl}/users`
);


}

// Create user
createUser(user: any) {


return this.http.post(
  `${this.baseUrl}/users`,
  user
);


}

// Delete user
deleteUser(email: string) {


return this.http.delete(
  `${this.baseUrl}/users/${email}`
);


}

// =====================================================
// PROJECTS
// =====================================================

// Get all projects
getProjects() {


return this.http.get(
  `${this.baseUrl}/projects/`
);


}

// Get project by ID
getProject(projectId: number) {


return this.http.get(
  `${this.baseUrl}/projects/${projectId}`
);


}

// Create project
createProject(project: any) {


return this.http.post(
  `${this.baseUrl}/projects/`,
  project
);


}

// Update project
updateProject(projectId: number, project: any) {


return this.http.put(
  `${this.baseUrl}/projects/${projectId}`,
  project
);


}

// Delete project
deleteProject(projectId: number) {


return this.http.delete(
  `${this.baseUrl}/projects/${projectId}`
);


}

// Update project status
updateProjectStatus(projectId: number, status: any) {


return this.http.put(
  `${this.baseUrl}/projects/${projectId}/status`,
  status
);


}

// Close project
closeProject(projectId: number) {


return this.http.put(
  `${this.baseUrl}/projects/${projectId}/close`,
  {}
);


}

// Project tracking
getProjectTracking(projectId: number) {


return this.http.get(
  `${this.baseUrl}/projects/${projectId}/tracking`
);


}

// =====================================================
// MILESTONES
// =====================================================

// Get milestones
getMilestones() {


return this.http.get(
  `${this.baseUrl}/milestones/`
);


}

// Create milestone
createMilestone(milestone: any) {


return this.http.post(
  `${this.baseUrl}/milestones/`,
  milestone
);


}

// Get milestone
getMilestone(milestoneId: number) {


return this.http.get(
  `${this.baseUrl}/milestones/${milestoneId}`
);


}

// Update milestone
updateMilestone(milestoneId: number, milestone: any) {


return this.http.put(
  `${this.baseUrl}/milestones/${milestoneId}`,
  milestone
);


}

// Delete milestone
deleteMilestone(milestoneId: number) {


return this.http.delete(
  `${this.baseUrl}/milestones/${milestoneId}`
);


}

// =====================================================
// RESOURCES
// =====================================================

// Get resources
getResources() {


return this.http.get(
  `${this.baseUrl}/resources/`
);


}

// Create resource
createResource(resource: any) {


return this.http.post(
  `${this.baseUrl}/resources/`,
  resource
);


}

// Get resource
getResource(resourceId: number) {


return this.http.get(
  `${this.baseUrl}/resources/${resourceId}`
);


}

// Update resource
updateResource(resourceId: number, resource: any) {


return this.http.put(
  `${this.baseUrl}/resources/${resourceId}`,
  resource
);


}

// Delete resource
deleteResource(resourceId: number) {


return this.http.delete(
  `${this.baseUrl}/resources/${resourceId}`
);


}

// Allocate resource
allocateResource(resourceId: number, data: any) {


return this.http.put(
  `${this.baseUrl}/resources/${resourceId}/allocate`,
  data
);


}

// Release resource
releaseResource(resourceId: number) {


return this.http.put(
  `${this.baseUrl}/resources/${resourceId}/release`,
  {}
);


}

// Resource utilization
getResourceUtilization(resourceId: number) {


return this.http.get(
  `${this.baseUrl}/resources/${resourceId}/utilization`
);


}

// =====================================================
// INVENTORY
// =====================================================

getInventory() {


return this.http.get(
  `${this.baseUrl}/inventory/`
);


}

createInventory(inventory: any) {


return this.http.post(
  `${this.baseUrl}/inventory/`,
  inventory
);


}

getInventoryById(inventoryId: number) {


return this.http.get(
  `${this.baseUrl}/inventory/${inventoryId}`
);


}

updateInventory(inventoryId: number, inventory: any) {


return this.http.put(
  `${this.baseUrl}/inventory/${inventoryId}`,
  inventory
);


}

deleteInventory(inventoryId: number) {


return this.http.delete(
  `${this.baseUrl}/inventory/${inventoryId}`
);


}

useInventory(inventoryId: number, data: any) {


return this.http.put(
  `${this.baseUrl}/inventory/${inventoryId}/use`,
  data
);


}

releaseInventory(inventoryId: number) {


return this.http.put(
  `${this.baseUrl}/inventory/${inventoryId}/release`,
  {}
);


}

getInventoryUtilization(inventoryId: number) {


return this.http.get(
  `${this.baseUrl}/inventory/${inventoryId}/utilization`
);


}

// =====================================================
// WORKERS
// =====================================================

getWorkers() {


return this.http.get(
  `${this.baseUrl}/workers/`
);


}

createWorker(worker: any) {


return this.http.post(
  `${this.baseUrl}/workers/`,
  worker
);


}

getWorker(workerId: number) {


return this.http.get(
  `${this.baseUrl}/workers/${workerId}`
);


}

updateWorker(workerId: number, worker: any) {


return this.http.put(
  `${this.baseUrl}/workers/${workerId}`,
  worker
);


}

deleteWorker(workerId: number) {


return this.http.delete(
  `${this.baseUrl}/workers/${workerId}`
);


}

useWorker(workerId: number, data: any) {


return this.http.put(
  `${this.baseUrl}/workers/${workerId}/use`,
  data
);


}

releaseWorker(workerId: number) {


return this.http.put(
  `${this.baseUrl}/workers/${workerId}/release`,
  {}
);


}

getWorkerUtilization(workerId: number) {


return this.http.get(
  `${this.baseUrl}/workers/${workerId}/utilization`
);


}

// =====================================================
// ATTENDANCE
// =====================================================

getAttendance() {


return this.http.get(
  `${this.baseUrl}/attendance/`
);


}

createAttendance(attendance: any) {


return this.http.post(
  `${this.baseUrl}/attendance/`,
  attendance
);


}

getAttendanceById(attendanceId: number) {


return this.http.get(
  `${this.baseUrl}/attendance/${attendanceId}`
);


}

updateAttendance(attendanceId: number, attendance: any) {


return this.http.put(
  `${this.baseUrl}/attendance/${attendanceId}`,
  attendance
);


}

deleteAttendance(attendanceId: number) {


return this.http.delete(
  `${this.baseUrl}/attendance/${attendanceId}`
);


}

useAttendance(attendanceId: number, data: any) {


return this.http.put(
  `${this.baseUrl}/attendance/${attendanceId}/use`,
  data
);


}

releaseAttendance(attendanceId: number) {


return this.http.put(
  `${this.baseUrl}/attendance/${attendanceId}/release`,
  {}
);


}

getAttendanceUtilization(attendanceId: number) {


return this.http.get(
  `${this.baseUrl}/attendance/${attendanceId}/utilization`
);


}

// =====================================================
// PROCUREMENT
// =====================================================

getProcurements() {


return this.http.get(
  `${this.baseUrl}/procurement/`
);


}

createProcurement(procurement: any) {


return this.http.post(
  `${this.baseUrl}/procurement/`,
  procurement
);


}

getProcurement(procurementId: number) {


return this.http.get(
  `${this.baseUrl}/procurement/${procurementId}`
);


}

updateProcurement(procurementId: number, procurement: any) {


return this.http.put(
  `${this.baseUrl}/procurement/${procurementId}`,
  procurement
);


}

deleteProcurement(procurementId: number) {


return this.http.delete(
  `${this.baseUrl}/procurement/${procurementId}`
);


}

useProcurement(procurementId: number, data: any) {


return this.http.put(
  `${this.baseUrl}/procurement/${procurementId}/use`,
  data
);


}

releaseProcurement(procurementId: number) {


return this.http.put(
  `${this.baseUrl}/procurement/${procurementId}/release`,
  {}
);


}

getProcurementUtilization(procurementId: number) {


return this.http.get(
  `${this.baseUrl}/procurement/${procurementId}/utilization`
);


}

// =====================================================
// NOTIFICATIONS
// =====================================================

getNotifications() {


return this.http.get(
  `${this.baseUrl}/notification/`
);


}

createNotification(notification: any) {


return this.http.post(
  `${this.baseUrl}/notification/`,
  notification
);


}

getNotification(notificationId: number) {


return this.http.get(
  `${this.baseUrl}/notification/${notificationId}`
);


}

updateNotification(notificationId: number, notification: any) {


return this.http.put(
  `${this.baseUrl}/notification/${notificationId}`,
  notification
);


}

deleteNotification(notificationId: number) {


return this.http.delete(
  `${this.baseUrl}/notification/${notificationId}`
);


}

// =====================================================
// REPORTS
// =====================================================

getReports() {


return this.http.get(
  `${this.baseUrl}/report/`
);


}

createReport(report: any) {


return this.http.post(
  `${this.baseUrl}/report/`,
  report
);


}

getReport(reportId: number) {


return this.http.get(
  `${this.baseUrl}/report/${reportId}`
);


}

updateReport(reportId: number, report: any) {


return this.http.put(
  `${this.baseUrl}/report/${reportId}`,
  report
);


}

deleteReport(reportId: number) {


return this.http.delete(
  `${this.baseUrl}/report/${reportId}`
);


}

// =====================================================
// ANALYTICS
// =====

getAnalytics() {


return this.http.get(
  `${this.baseUrl}/analytics/`
);


}

getProjectProgress() {


return this.http.get(
  `${this.baseUrl}/analytics/project-progress`
);


}

getResourceUtilizationAnalytics() {


return this.http.get(
  `${this.baseUrl}/analytics/resource-utilization`
);


}

getInventoryStatus() {


return this.http.get(
  `${this.baseUrl}/analytics/inventory-status`
);


}

getProcurementStatus() {


return this.http.get(
  `${this.baseUrl}/analytics/procurement-status`
);


}

getWorkerAttendance() {


return this.http.get(
  `${this.baseUrl}/analytics/worker-attendance`
);


}

getProjectSummary() {


return this.http.get(
  `${this.baseUrl}/analytics/project-summary`
);


}

getReportSummary() {

return this.http.get(
  `${this.baseUrl}/analytics/report-summary`
);


}

}
