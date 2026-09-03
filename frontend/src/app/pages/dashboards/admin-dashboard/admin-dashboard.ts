import { CommonModule } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  OnInit
} from '@angular/core';
import {
  HttpClient,
  HttpHeaders
} from '@angular/common/http';
import {
  Router,
  RouterLink
} from '@angular/router';

// =====================================================
// INTERFACES
// =====================================================

interface AdminInfo {
  id: number;
  name: string;
  email: string;
}

interface UserRoleAnalytics {
  ADMIN?: number;
  PROJECT_MANAGER?: number;
  SITE_ENGINEER?: number;
  CONTRACTOR?: number;
  WORKER?: number;
  CLIENT?: number;
  [key: string]: number | undefined;
}

interface UserAnalytics {
  total_users: number;
  active_users: number;
  inactive_users: number;
  by_role: UserRoleAnalytics;
}

interface ProjectDetail {
  project_id: number;
  project_name: string;
  status: string;
  progress: number;
  manager_id: number | null;
}

interface ProjectAnalytics {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  pending_projects: number;
  details: ProjectDetail[];
}

interface SystemAnalytics {
  total_workers: number;
  total_resources: number;
  total_procurements: number;
  total_reports: number;
}

interface ReportDetail {
  id?: number;
  title?: string;
  name?: string;
  status?: string;
  created_at?: string;
  createdAt?: string;
  type?: string;
}

interface ReportsAnalytics {
  total_reports: number;
  details: ReportDetail[];
}

interface ActivityDetail {
  id?: number;

  action?: string;
  activity?: string;
  description?: string;
  title?: string;
  message?: string;

  user?: string;
  user_name?: string;

  created_at?: string;
  createdAt?: string;
  timestamp?: string;
}

interface AdminDashboardResponse {
  role: string;
  admin: AdminInfo;
  users: UserAnalytics;
  projects: ProjectAnalytics;
  system_analytics: SystemAnalytics;
  reports: ReportsAnalytics;
  activities: ActivityDetail[];
}

// =====================================================
// COMPONENT
// =====================================================

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,

  imports: [
    CommonModule,
    RouterLink
  ],

  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css'
})
export class AdminDashboard implements OnInit {

  // =====================================================
  // API URL
  // =====================================================

  private readonly API_URL =
    'http://127.0.0.1:8000';

  // =====================================================
  // STATE
  // =====================================================

  loading = true;

  errorMessage = '';

  dashboard: AdminDashboardResponse | null = null;

  sidebarOpen = false;

  selectedProject: ProjectDetail | null = null;

  currentDate = new Date();

  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(
    private http: HttpClient,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {

    console.log(
      'Admin Dashboard initialized'
    );

    this.loadDashboard();
  }

  // =====================================================
  // LOAD DASHBOARD
  // =====================================================

  loadDashboard(): void {

    console.log(
      'Starting Admin Dashboard API...'
    );

    // Start loading
    this.loading = true;

    this.errorMessage = '';

    // Clear previous data only when manually refreshing
    // this.dashboard = null;

    // ===================================================
    // GET JWT TOKEN
    // ===================================================

    const token =
      localStorage.getItem('access_token') ||
      localStorage.getItem('token');

    console.log(
      'Dashboard token exists:',
      !!token
    );

    // ===================================================
    // TOKEN NOT FOUND
    // ===================================================

    if (!token) {

      console.error(
        'JWT token not found.'
      );

      this.loading = false;

      this.errorMessage =
        'Login session not found. Please login again.';

      this.cdr.detectChanges();

      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 500);

      return;
    }

    // ===================================================
    // HTTP HEADERS
    // ===================================================

    const headers =
      new HttpHeaders({
        Authorization: `Bearer ${token}`,
        Accept: 'application/json'
      });

    console.log(
      'Authorization header created.'
    );

    // ===================================================
    // API REQUEST
    // ===================================================

    this.http
      .get<AdminDashboardResponse>(
        `${this.API_URL}/dashboard/admin`,
        {
          headers
        }
      )
      .subscribe({

        // =================================================
        // SUCCESS
        // =================================================

        next: (
          response: AdminDashboardResponse
        ) => {

          console.log(
            '================================='
          );

          console.log(
            'Admin Dashboard Response:',
            response
          );

          console.log(
            '================================='
          );

          // -----------------------------------------------
          // Validate response
          // -----------------------------------------------

          if (!response) {

            console.error(
              'Empty dashboard response.'
            );

            this.dashboard = null;

            this.errorMessage =
              'Dashboard returned empty data.';

            this.loading = false;

            this.cdr.detectChanges();

            return;
          }

          // -----------------------------------------------
          // Assign dashboard
          // -----------------------------------------------

          this.dashboard = response;

          console.log(
            'Dashboard assigned:',
            this.dashboard
          );

          // -----------------------------------------------
          // Select first project
          // -----------------------------------------------

          if (
            response.projects &&
            Array.isArray(
              response.projects.details
            ) &&
            response.projects.details.length > 0
          ) {

            this.selectedProject =
              response.projects.details[0];

          } else {

            this.selectedProject = null;
          }

          // -----------------------------------------------
          // IMPORTANT
          // -----------------------------------------------

          this.loading = false;

          this.errorMessage = '';

          console.log(
            'Loading after API:',
            this.loading
          );

          console.log(
            'Dashboard ready:',
            this.dashboard
          );

          // -----------------------------------------------
          // Force Angular UI update
          // -----------------------------------------------

          this.cdr.detectChanges();

        },

        // =================================================
        // ERROR
        // =================================================

        error: (error) => {

          console.error(
            '================================='
          );

          console.error(
            'Admin Dashboard Error:',
            error
          );

          console.error(
            'Status:',
            error?.status
          );

          console.error(
            'Message:',
            error?.message
          );

          console.error(
            'Error body:',
            error?.error
          );

          console.error(
            '================================='
          );

          // IMPORTANT
          // Always stop loading on error

          this.loading = false;

          // =================================================
          // 401
          // =================================================

          if (error?.status === 401) {

            this.errorMessage =
              'Authentication failed. Your login session may have expired. Please login again.';

            localStorage.removeItem(
              'access_token'
            );

            localStorage.removeItem(
              'token'
            );

            localStorage.removeItem(
              'user'
            );

            localStorage.removeItem(
              'role'
            );

            this.cdr.detectChanges();

            setTimeout(() => {

              this.router.navigate([
                '/login'
              ]);

            }, 800);

            return;
          }

          // =================================================
          // 403
          // =================================================

          if (error?.status === 403) {

            this.errorMessage =
              'You are not authorized to access the Admin Dashboard.';

            this.cdr.detectChanges();

            return;
          }

          // =================================================
          // 404
          // =================================================

          if (error?.status === 404) {

            this.errorMessage =
              'Admin Dashboard API endpoint was not found. Check /dashboard/admin in FastAPI.';

            this.cdr.detectChanges();

            return;
          }

          // =================================================
          // 0
          // =================================================

          if (error?.status === 0) {

            this.errorMessage =
              'Backend server is not connected. Start FastAPI on port 8000.';

            this.cdr.detectChanges();

            return;
          }

          // =================================================
          // 500
          // =================================================

          if (
            error?.status >= 500
          ) {

            this.errorMessage =
              'FastAPI server returned a server error. Check the backend terminal.';

            this.cdr.detectChanges();

            return;
          }

          // =================================================
          // OTHER
          // =================================================

          this.errorMessage =
            'Unable to load dashboard data. Please try again.';

          this.cdr.detectChanges();
        }

      });
  }

  // =====================================================
  // SIDEBAR
  // =====================================================

  toggleSidebar(): void {

    this.sidebarOpen =
      !this.sidebarOpen;
  }

  closeSidebar(): void {

    this.sidebarOpen = false;
  }

  // =====================================================
  // LOGOUT
  // =====================================================

  logout(): void {

    localStorage.removeItem(
      'token'
    );

    localStorage.removeItem(
      'access_token'
    );

    localStorage.removeItem(
      'user'
    );

    localStorage.removeItem(
      'role'
    );

    this.router.navigate([
      '/login'
    ]);
  }

  // =====================================================
  // ADMIN INFORMATION
  // =====================================================

  get adminName(): string {

    return (
      this.dashboard?.admin?.name ||
      'Administrator'
    );
  }

  get adminEmail(): string {

    return (
      this.dashboard?.admin?.email ||
      ''
    );
  }

  get adminId(): number {

    return (
      this.dashboard?.admin?.id ||
      0
    );
  }

  get adminRole(): string {

    return (
      this.dashboard?.role ||
      'ADMIN'
    );
  }

  // =====================================================
  // ADMIN INITIALS
  // =====================================================

  get adminInitials(): string {

    const name =
      this.adminName.trim();

    if (!name) {
      return 'A';
    }

    const parts =
      name.split(/\s+/);

    if (parts.length === 1) {

      return parts[0]
        .charAt(0)
        .toUpperCase();
    }

    return (
      parts[0].charAt(0) +
      parts[parts.length - 1].charAt(0)
    ).toUpperCase();
  }

  // =====================================================
  // USERS
  // =====================================================

  get totalUsers(): number {

    return (
      this.dashboard?.users?.total_users ||
      0
    );
  }

  get activeUsers(): number {

    return (
      this.dashboard?.users?.active_users ||
      0
    );
  }

  get inactiveUsers(): number {

    return (
      this.dashboard?.users?.inactive_users ||
      0
    );
  }

  // =====================================================
  // USER PERCENTAGES
  // =====================================================

  get activeUserPercentage(): number {

    if (!this.totalUsers) {
      return 0;
    }

    return Math.round(
      (this.activeUsers /
        this.totalUsers) * 100
    );
  }

  get inactiveUserPercentage(): number {

    if (!this.totalUsers) {
      return 0;
    }

    return Math.round(
      (this.inactiveUsers /
        this.totalUsers) * 100
    );
  }

  // =====================================================
  // ROLE ANALYTICS
  // =====================================================

  get roleAnalytics() {

    const roles =
      this.dashboard?.users?.by_role;

    if (!roles) {
      return [];
    }

    return [

      {
        key: 'ADMIN',
        label: 'Administrators',
        value: roles.ADMIN || 0
      },

      {
        key: 'PROJECT_MANAGER',
        label: 'Project Managers',
        value:
          roles.PROJECT_MANAGER || 0
      },

      {
        key: 'SITE_ENGINEER',
        label: 'Site Engineers',
        value:
          roles.SITE_ENGINEER || 0
      },

      {
        key: 'CONTRACTOR',
        label: 'Contractors',
        value:
          roles.CONTRACTOR || 0
      },

      {
        key: 'WORKER',
        label: 'Workers',
        value:
          roles.WORKER || 0
      },

      {
        key: 'CLIENT',
        label: 'Clients',
        value:
          roles.CLIENT || 0
      }

    ];
  }

  getRolePercentage(
    value: number
  ): number {

    if (!this.totalUsers) {
      return 0;
    }

    return Math.round(
      (value / this.totalUsers) * 100
    );
  }

  // =====================================================
  // PROJECT ANALYTICS
  // =====================================================

  get totalProjects(): number {

    return (
      this.dashboard?.projects?.total_projects ||
      0
    );
  }

  get activeProjects(): number {

    return (
      this.dashboard?.projects?.active_projects ||
      0
    );
  }

  get completedProjects(): number {

    return (
      this.dashboard?.projects?.completed_projects ||
      0
    );
  }

  get pendingProjects(): number {

    return (
      this.dashboard?.projects?.pending_projects ||
      0
    );
  }

  get projectDetails(): ProjectDetail[] {

    return (
      this.dashboard?.projects?.details ||
      []
    );
  }

  // =====================================================
  // PROJECT PERCENTAGES
  // =====================================================

  get activeProjectPercentage(): number {

    if (!this.totalProjects) {
      return 0;
    }

    return Math.round(
      (this.activeProjects /
        this.totalProjects) * 100
    );
  }

  get completedProjectPercentage(): number {

    if (!this.totalProjects) {
      return 0;
    }

    return Math.round(
      (this.completedProjects /
        this.totalProjects) * 100
    );
  }

  get pendingProjectPercentage(): number {

    if (!this.totalProjects) {
      return 0;
    }

    return Math.round(
      (this.pendingProjects /
        this.totalProjects) * 100
    );
  }

  // =====================================================
  // SYSTEM ANALYTICS
  // =====================================================

  get totalWorkers(): number {

    return (
      this.dashboard
        ?.system_analytics
        ?.total_workers ||
      0
    );
  }

  get totalResources(): number {

    return (
      this.dashboard
        ?.system_analytics
        ?.total_resources ||
      0
    );
  }

  get totalProcurements(): number {

    return (
      this.dashboard
        ?.system_analytics
        ?.total_procurements ||
      0
    );
  }

  get totalReports(): number {

    return (
      this.dashboard
        ?.system_analytics
        ?.total_reports ||
      0
    );
  }

  get totalRecords(): number {

    return (
      this.totalUsers +
      this.totalProjects +
      this.totalWorkers +
      this.totalResources
    );
  }

  // =====================================================
  // REPORTS
  // =====================================================

  get reports(): ReportDetail[] {

    return (
      this.dashboard?.reports?.details ||
      []
    );
  }

  get reportCount(): number {

    return (
      this.dashboard?.reports?.total_reports ||
      this.reports.length
    );
  }

  getReportTitle(
    report: ReportDetail
  ): string {

    return (
      report.title ||
      report.name ||
      'System Report'
    );
  }

  getReportDate(
    report: ReportDetail
  ): string {

    return (
      report.created_at ||
      report.createdAt ||
      'Recently generated'
    );
  }

  getReportStatus(
    report: ReportDetail
  ): string {

    return (
      report.status ||
      'Available'
    );
  }

  getReportStatusClass(
    report: ReportDetail
  ): string {

    const status =
      this.getReportStatus(report)
        .toLowerCase();

    if (
      status.includes('complete') ||
      status.includes('approved') ||
      status.includes('available')
    ) {

      return 'status-completed';
    }

    if (
      status.includes('pending') ||
      status.includes('processing')
    ) {

      return 'status-pending';
    }

    if (
      status.includes('reject') ||
      status.includes('failed')
    ) {

      return 'status-danger';
    }

    return 'status-default';
  }

  // =====================================================
  // ACTIVITIES
  // =====================================================

  get activities(): ActivityDetail[] {

    return (
      this.dashboard?.activities ||
      []
    );
  }

  getActivityText(
    activity: ActivityDetail
  ): string {

    return (
      activity.description ||
      activity.message ||
      activity.action ||
      activity.activity ||
      activity.title ||
      'System activity'
    );
  }

  getActivityUser(
    activity: ActivityDetail
  ): string {

    return (
      activity.user_name ||
      activity.user ||
      'System User'
    );
  }

  getActivityDate(
    activity: ActivityDetail
  ): string {

    return (
      activity.created_at ||
      activity.createdAt ||
      activity.timestamp ||
      'Recently'
    );
  }

  // =====================================================
  // PROJECT PROGRESS
  // =====================================================

  getProjectProgress(
    project: ProjectDetail
  ): number {

    const progress =
      Number(project?.progress);

    if (
      Number.isNaN(progress)
    ) {
      return 0;
    }

    return Math.min(
      Math.max(progress, 0),
      100
    );
  }

  // =====================================================
  // SELECT PROJECT
  // =====================================================

  selectProject(
    project: ProjectDetail
  ): void {

    this.selectedProject =
      project;
  }

  get selectedProjectProgress(): number {

    if (!this.selectedProject) {
      return 0;
    }

    return this.getProjectProgress(
      this.selectedProject
    );
  }

  // =====================================================
  // PROJECT STATUS
  // =====================================================

  getStatusClass(
    status: string
  ): string {

    if (!status) {
      return 'status-default';
    }

    const value =
      status.toLowerCase();

    if (
      value.includes('complete') ||
      value.includes('closed')
    ) {

      return 'status-completed';
    }

    if (
      value.includes('active') ||
      value.includes('progress') ||
      value.includes('ongoing')
    ) {

      return 'status-active';
    }

    if (
      value.includes('pending') ||
      value.includes('planned')
    ) {

      return 'status-pending';
    }

    if (
      value.includes('cancel') ||
      value.includes('reject')
    ) {

      return 'status-danger';
    }

    return 'status-default';
  }

  getProjectStatusLabel(
    status: string
  ): string {

    return status || 'Unknown';
  }

  // =====================================================
  // PROJECT MANAGER
  // =====================================================

  getProjectManagerId(
    project: ProjectDetail
  ): string {

    if (
      project.manager_id === null ||
      project.manager_id === undefined
    ) {

      return 'Not assigned';
    }

    return `Manager #${project.manager_id}`;
  }

  // =====================================================
  // REFRESH
  // =====================================================

  refreshDashboard(): void {

    console.log(
      'Refreshing dashboard...'
    );

    this.loadDashboard();
  }

  retry(): void {

    this.loadDashboard();
  }

  // =====================================================
  // NAVIGATION
  // =====================================================

  navigateTo(
    path: string
  ): void {

    this.closeSidebar();

    this.router.navigate([
      path
    ]);
  }

  // =====================================================
  // OPEN PROJECT
  // =====================================================

  openProject(
    project: ProjectDetail
  ): void {

    this.selectedProject =
      project;

    this.router.navigate([
      '/projects/project-details',
      project.project_id
    ]);
  }

  // =====================================================
  // OPEN REPORTS
  // =====================================================

  openReports(): void {

    this.router.navigate([
      '/reports'
    ]);
  }

  // =====================================================
  // OPEN USERS
  // =====================================================

  openUsers(): void {

    this.router.navigate([
      '/user-management'
    ]);
  }

  // =====================================================
  // OPEN PROJECTS
  // =====================================================

  openProjects(): void {

    this.router.navigate([
      '/projects'
    ]);
  }

  // =====================================================
  // OPEN PROCUREMENT
  // =====================================================

  openProcurement(): void {

    this.router.navigate([
      '/procurement'
    ]);
  }

  // =====================================================
  // OPEN RESOURCES
  // =====================================================

  openResources(): void {

    this.router.navigate([
      '/resources/resource-allocation'
    ]);
  }

  // =====================================================
  // OPEN WORKFORCE
  // =====================================================

  openWorkforce(): void {

    this.router.navigate([
      '/workforce'
    ]);
  }

  // =====================================================
  // OPEN ANALYTICS
  // =====================================================

  openAnalytics(): void {

    this.router.navigate([
      '/analytics'
    ]);
  }

  // =====================================================
  // ADMIN CHECK
  // =====================================================

  isAdmin(): boolean {

    return (
      this.adminRole
        .toUpperCase() ===
      'ADMIN'
    );
  }

  // =====================================================
  // DATE FORMAT
  // =====================================================

  formatDate(
    value: string | Date
  ): string {

    if (!value) {
      return '';
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return String(value);
    }

    return date.toLocaleDateString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }
    );
  }

  // =====================================================
  // DATE + TIME FORMAT
  // =====================================================

  formatDateTime(
    value: string | Date
  ): string {

    if (!value) {
      return '';
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return String(value);
    }

    return date.toLocaleString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
    );
  }
}