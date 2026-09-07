import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NavigationEnd, Router, RouterLink } from '@angular/router';
import { catchError, filter, finalize, forkJoin, of, Subject, takeUntil, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

interface ProjectRow {
  id: number;
  project_name: string;
  status: string;
  start_date?: string;
  end_date?: string;
  progress: number;
  estimated_budget?: number | null;
  utilized_budget?: number | null;
  remaining_budget?: number | null;
  manager_id?: number | null;
}

@Component({
  selector: 'app-project-manager-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './project-manager-dashboard.html',
  styleUrl: './project-manager-dashboard.css'
})
export class ProjectManagerDashboard implements OnInit, OnDestroy {
  loading = true;
  error = '';
  projects: ProjectRow[] = [];
  selectedProjectId: number | null = null;
  resources: any[] = [];
  workforce: any[] = [];
  procurements: any[] = [];
  progressRows: any[] = [];
  budgetSummary: any = null;

  private readonly destroy$ = new Subject<void>();
  private readonly focusHandler = () => this.loadDashboard(false);

  constructor(private api: Api, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit(): void {
    this.loadDashboard();
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      filter(event => event.urlAfterRedirects.includes('/project-manager-dashboard')),
      takeUntil(this.destroy$)
    ).subscribe(() => this.loadDashboard(false));
    window.addEventListener('focus', this.focusHandler);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    window.removeEventListener('focus', this.focusHandler);
  }

  loadDashboard(showSpinner = true): void {
    if (showSpinner) {
      this.loading = true;
    }
    this.error = '';
    this.cdr.detectChanges();

    forkJoin({
      projects: this.api.getProjects().pipe(timeout(10000), catchError(() => of([]))),
      progress: this.api.getProjectProgress().pipe(timeout(10000), catchError(() => of([]))),
      resources: this.api.getResourceUtilizationAnalytics().pipe(timeout(10000), catchError(() => of([]))),
      attendance: this.api.getWorkerAttendance().pipe(timeout(10000), catchError(() => of([]))),
      procurements: this.api.getProcurementStatus().pipe(timeout(10000), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: data => {
        this.progressRows = Array.isArray(data.progress) ? data.progress : [];
        const progressMap = new Map<number, number>(this.progressRows.map((row: any) => [Number(row.project_id), this.pct(row.progress)]));
        const currentUser = this.currentUser();
        const rows = Array.isArray(data.projects) ? data.projects : [];
        this.projects = rows
          .filter((project: any) => {
            const manager = project.manager_id ?? project.project_manager_id ?? project.assigned_manager_id;
            return manager == null || currentUser.id == null || Number(manager) === Number(currentUser.id);
          })
          .map((project: any) => {
            const estimated = this.numberOrNull(project.estimated_budget ?? project.budget ?? project.planned_budget);
            const utilized = this.numberOrNull(project.utilized_budget ?? project.actual_cost ?? project.spent_amount ?? project.total_expense);
            return {
              id: Number(project.id),
              project_name: project.project_name || project.name || 'Unnamed project',
              status: project.status || 'Planning',
              start_date: project.start_date,
              end_date: project.end_date,
              progress: progressMap.get(Number(project.id)) ?? this.pct(project.progress),
              estimated_budget: estimated,
              utilized_budget: utilized,
              remaining_budget: estimated != null && utilized != null ? Math.max(0, estimated - utilized) : null,
              manager_id: project.manager_id ?? project.project_manager_id ?? null
            } as ProjectRow;
          });
        this.resources = Array.isArray(data.resources) ? data.resources : [];
        this.workforce = Array.isArray(data.attendance) ? data.attendance : [];
        this.procurements = Array.isArray(data.procurements) ? data.procurements : [];
        if (!this.selectedProjectId || !this.projects.some(p => p.id === Number(this.selectedProjectId))) {
          this.selectedProjectId = this.projects[0]?.id ?? null;
        }
        this.loadBudgetSummary();
      },
      error: () => {
        this.error = 'Unable to load the Project Manager dashboard. Check that the backend is running.';
      }
    });
  }

  onProjectChange(): void { this.loadBudgetSummary(); }

  loadBudgetSummary(): void {
    this.budgetSummary = null;
    if (!this.selectedProjectId) {
      this.cdr.detectChanges();
      return;
    }
    this.api.getBudgetSummary(Number(this.selectedProjectId)).pipe(
      timeout(10000),
      catchError(() => of(null)),
      finalize(() => this.cdr.detectChanges())
    ).subscribe(summary => this.budgetSummary = summary);
  }

  get dashboardBudgetPlanned(): number | null { return this.numberOrNull(this.budgetSummary?.total_budget ?? this.selectedProject?.estimated_budget); }
  get dashboardBudgetSpent(): number | null { return this.numberOrNull(this.budgetSummary?.amount_spent ?? this.budgetSummary?.actual_cost ?? this.selectedProject?.utilized_budget); }
  get dashboardBudgetRemaining(): number | null {
    const explicit = this.numberOrNull(this.budgetSummary?.remaining_budget);
    if (explicit != null) return explicit;
    const planned = this.dashboardBudgetPlanned, spent = this.dashboardBudgetSpent;
    return planned != null && spent != null ? Math.max(0, planned - spent) : null;
  }

  get selectedProject(): ProjectRow | null { return this.projects.find(p => p.id === Number(this.selectedProjectId)) || null; }
  get projectResources(): any[] { return this.filterByProject(this.resources); }
  get projectWorkforce(): any[] { return this.filterByProject(this.workforce); }
  get projectProcurements(): any[] { return this.filterByProject(this.procurements); }
  get resourceUtilization(): number {
    const rows = this.projectResources;
    if (!rows.length) return 0;
    const explicit = rows.map(r => Number(r.utilization ?? r.utilization_percentage)).filter(Number.isFinite);
    if (explicit.length) return Math.round(explicit.reduce((a, b) => a + b, 0) / explicit.length);
    const total = rows.reduce((s, r) => s + (Number(r.total_quantity ?? r.quantity) || 0), 0);
    const allocated = rows.reduce((s, r) => s + (Number(r.allocated_quantity ?? r.allocated) || 0), 0);
    return total > 0 ? Math.round((allocated / total) * 100) : 0;
  }
  get attendanceAverage(): number {
    const values = this.projectWorkforce.map(r => Number(r.attendance_percentage)).filter(Number.isFinite);
    return values.length ? Math.round(values.reduce((a, b) => a + b, 0) / values.length) : 0;
  }
  get pendingProcurements(): number { return this.projectProcurements.filter(r => /pending|requested|approval/i.test(String(r.status || ''))).length; }

  pct(value: any): number { return Math.max(0, Math.min(100, Number(value) || 0)); }
  money(value: number | null | undefined): string { return value == null ? '—' : `₹${Number(value).toLocaleString('en-IN')}`; }
  private numberOrNull(value: any): number | null { const n = Number(value); return value === '' || value == null || !Number.isFinite(n) ? null : n; }
  private currentUser(): any { try { return JSON.parse(localStorage.getItem('currentUser') || '{}'); } catch { return {}; } }
  private filterByProject(rows: any[]): any[] {
    if (!this.selectedProjectId) return rows;
    const withProject = rows.filter(row => row.project_id != null || row.project?.id != null);
    if (!withProject.length) return rows;
    return rows.filter(row => Number(row.project_id ?? row.project?.id) === Number(this.selectedProjectId));
  }
}
