import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, map, Observable, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './analytics.html',
  styleUrl: './analytics.css'
})
export class Analytics implements OnInit {
  loading = false;
  refreshing = false;
  error = '';
  role = '';
  projects: any[] = [];
  selectedProjectId: number | null = null;
  summary: any = this.emptySummary();
  projectProgress: any[] = [];
  resourceUtilization: any[] = [];
  inventoryStatus: any[] = [];
  procurementStatus: any[] = [];
  workerAttendance: any[] = [];
  reportSummary: any[] = [];

  constructor(
    private api: Api,
    private cdr: ChangeDetectorRef,
    private zone: NgZone
  ) {}

  ngOnInit(): void {
    this.role = this.currentRole();
    this.load();
  }

  load(): void {
    this.loading = true;
    this.refreshing = true;
    this.error = '';
    this.forceRefresh();

    forkJoin({
      projects: this.safeArray(this.api.getProjects(), 'projects'),
      summary: this.safeObject(this.api.getAnalytics(), 'summary'),
      projectProgress: this.safeArray(this.api.getProjectProgress(), 'project progress'),
      resourceUtilization: this.safeArray(this.api.getResourceUtilizationAnalytics(), 'resource utilization'),
      inventoryStatus: this.safeArray(this.api.getInventoryStatus(), 'inventory status'),
      procurementStatus: this.safeArray(this.api.getProcurementStatus(), 'procurement status'),
      workerAttendance: this.safeArray(this.api.getWorkerAttendance(), 'worker attendance'),
      reportSummary: this.safeArray(this.api.getReportSummary(), 'report summary')
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.refreshing = false;
        this.forceRefresh();
      })
    ).subscribe({
      next: data => {
        const user = this.currentUser();
        const allProjects = data.projects.map(project => this.normalizeProject(project));
        this.projects = this.role === 'PROJECT_MANAGER'
          ? allProjects.filter((project: any) => {
              const manager = project.manager_id ?? project.project_manager_id ?? project.assigned_manager_id;
              return manager == null || user.id == null || Number(manager) === Number(user.id);
            })
          : allProjects;

        if (this.selectedProjectId && !this.projects.some(project => Number(project.id) === Number(this.selectedProjectId))) {
          this.selectedProjectId = null;
        }

        this.summary = this.normalizeSummary(data.summary);
        this.projectProgress = data.projectProgress.map(row => this.normalizeProjectProgress(row));
        this.resourceUtilization = data.resourceUtilization.map(row => this.normalizeResource(row));
        this.inventoryStatus = data.inventoryStatus.map(row => this.normalizeInventory(row));
        this.procurementStatus = data.procurementStatus.map(row => this.normalizeProcurement(row));
        this.workerAttendance = data.workerAttendance.map(row => this.normalizeWorkerAttendance(row));
        this.reportSummary = data.reportSummary;

        if (!this.projects.length) {
          this.error = 'No accessible projects found. Create or assign a project to see project-level analytics.';
        }
      },
      error: () => {
        this.projects = [];
        this.summary = this.emptySummary();
        this.projectProgress = [];
        this.resourceUtilization = [];
        this.inventoryStatus = [];
        this.procurementStatus = [];
        this.workerAttendance = [];
        this.reportSummary = [];
        this.error = 'Unable to load analytics. Check that the backend is running and login token is valid.';
      }
    });
  }

  get filteredProgress(): any[] { return this.filterProject(this.projectProgress); }
  get filteredResources(): any[] { return this.filterProject(this.resourceUtilization); }
  get filteredProcurement(): any[] { return this.filterProject(this.procurementStatus); }
  get filteredWorkforce(): any[] { return this.filterProject(this.workerAttendance); }

  pct(value: any): number {
    const numberValue = Math.round(Number(value) || 0);
    return Math.max(0, Math.min(100, numberValue));
  }

  roleTitle(): string {
    return this.role === 'ADMIN' ? 'System Analytics' : 'Project Analytics';
  }

  private safeArray(source$: Observable<any>, label: string): Observable<any[]> {
    return source$.pipe(
      timeout({ first: 5000 }),
      map(value => this.toArray(value)),
      catchError(error => {
        console.warn(`Analytics: ${label} request failed`, error);
        return of([]);
      })
    );
  }

  private safeObject(source$: Observable<any>, label: string): Observable<any> {
    return source$.pipe(
      timeout({ first: 5000 }),
      map(value => value || {}),
      catchError(error => {
        console.warn(`Analytics: ${label} request failed`, error);
        return of({});
      })
    );
  }

  private toArray(value: any): any[] {
    if (Array.isArray(value)) return value;
    if (Array.isArray(value?.data)) return value.data;
    if (Array.isArray(value?.items)) return value.items;
    if (Array.isArray(value?.results)) return value.results;
    if (Array.isArray(value?.projects)) return value.projects;
    if (Array.isArray(value?.workers)) return value.workers;
    return [];
  }

  private filterProject(rows: any[]): any[] {
    if (!this.selectedProjectId) return rows;
    const projectRows = rows.filter(row => row.project_id != null || row.project?.id != null || row.id != null);
    if (!projectRows.length) return rows;
    return rows.filter(row => Number(row.project_id ?? row.project?.id ?? row.id) === Number(this.selectedProjectId));
  }

  private normalizeProject(project: any): any {
    return {
      ...project,
      id: Number(project?.id ?? project?.project_id ?? project?.projectId),
      project_name: project?.project_name || project?.name || project?.title || 'Unnamed Project'
    };
  }

  private normalizeSummary(summary: any): any {
    const fallback = this.emptySummary();
    return {
      projects: { ...fallback.projects, ...(summary?.projects || {}) },
      workers: { ...fallback.workers, ...(summary?.workers || {}) },
      resources: { ...fallback.resources, ...(summary?.resources || {}) },
      inventory: { ...fallback.inventory, ...(summary?.inventory || {}) },
      procurements: { ...fallback.procurements, ...(summary?.procurements || {}) }
    };
  }

  private normalizeProjectProgress(row: any): any {
    const totalMilestones = Number(row?.total_milestones ?? row?.totalMilestones ?? row?.milestone_count ?? 0);
    let completedMilestones = Number(row?.completed_milestones ?? row?.completedMilestones ?? row?.completed_count ?? 0);
    let progress = Number(
      row?.progress ??
      row?.progress_percentage ??
      row?.completion_percentage ??
      row?.overall_progress ??
      row?.percentage ??
      0
    );

    if ((!progress || progress <= 0) && totalMilestones > 0 && completedMilestones > 0) {
      progress = (completedMilestones / totalMilestones) * 100;
    }

    progress = this.pct(progress);

    // Some analytics APIs return overall project progress but not completed
    // milestone count. In that case, avoid displaying a confusing "0 / 3"
    // label beside a non-zero progress bar.
    let progressNote = '';
    if (totalMilestones > 0 && completedMilestones > 0) {
      progressNote = `${completedMilestones} / ${totalMilestones} milestones completed`;
    } else if (totalMilestones > 0) {
      progressNote = `${totalMilestones} milestones tracked`;
    } else {
      progressNote = 'Overall project progress';
    }

    return {
      ...row,
      project_id: Number(row?.project_id ?? row?.projectId ?? row?.id),
      project_name: row?.project_name || row?.name || 'Project',
      progress,
      completed_milestones: completedMilestones,
      total_milestones: totalMilestones,
      progress_note: progressNote
    };
  }

  private normalizeResource(row: any): any {
    return {
      ...row,
      project_id: row?.project_id ?? row?.project?.id ?? null,
      resource_name: row?.resource_name || row?.name || 'Resource',
      utilization: Number(row?.utilization ?? row?.utilization_percentage ?? 0)
    };
  }

  private normalizeInventory(row: any): any {
    return {
      ...row,
      item_name: row?.item_name || row?.material_name || row?.name || 'Item',
      remaining: Number(row?.remaining ?? row?.quantity ?? 0)
    };
  }

  private normalizeProcurement(row: any): any {
    return {
      ...row,
      project_id: row?.project_id ?? row?.project?.id ?? null,
      item_name: row?.item_name || row?.title || row?.name || 'Procurement item',
      status: row?.status || 'Pending'
    };
  }

  private normalizeWorkerAttendance(row: any): any {
    return {
      ...row,
      project_id: row?.project_id ?? row?.project?.id ?? null,
      worker_name: row?.worker_name || row?.name || 'Worker',
      attendance_percentage: Number(row?.attendance_percentage ?? row?.percentage ?? 0)
    };
  }

  private emptySummary(): any {
    return {
      projects: { total: 0, active: 0, completed: 0, pending: 0 },
      workers: { total: 0, present: 0, absent: 0 },
      resources: { total: 0 },
      inventory: { total: 0 },
      procurements: { total: 0 }
    };
  }

  private currentRole(): string {
    return String(this.currentUser()?.role || '').toUpperCase();
  }

  private currentUser(): any {
    try {
      return JSON.parse(localStorage.getItem('currentUser') || '{}');
    } catch {
      return {};
    }
  }

  private forceRefresh(): void {
    this.zone.run(() => {
      setTimeout(() => this.cdr.detectChanges(), 0);
    });
  }
}
