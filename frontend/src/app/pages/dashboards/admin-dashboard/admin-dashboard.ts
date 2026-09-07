import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { Router, RouterLink, NavigationEnd } from '@angular/router';
import { catchError, filter, finalize, forkJoin, of, Subject, takeUntil, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

interface ProjectRow {
  id: number;
  project_name: string;
  status: string;
  progress: number;
  manager_id?: number | null;
  location?: string;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, AppSidebarComponent],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css'
})
export class AdminDashboard implements OnInit, OnDestroy {
  loading = true;
  error = '';
  users: any[] = [];
  projects: ProjectRow[] = [];
  reports: any[] = [];
  activities: any[] = [];
  analytics: any = {};
  roleCounts: { role: string; count: number }[] = [];

  private readonly destroy$ = new Subject<void>();
  private readonly focusHandler = () => this.loadDashboard(false);

  summary = {
    users: 0,
    projects: 0,
    activeProjects: 0,
    completedProjects: 0,
    workers: 0,
    resources: 0,
    procurements: 0,
    reports: 0
  };

  constructor(private api: Api, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit(): void {
    this.loadDashboard();
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      filter(event => event.urlAfterRedirects.includes('/admin-dashboard')),
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
      analytics: this.api.getAnalytics().pipe(timeout(10000), catchError(() => of({}))),
      users: this.api.getUsers().pipe(timeout(10000), catchError(() => of([]))),
      projects: this.api.getProjects().pipe(timeout(10000), catchError(() => of([]))),
      progress: this.api.getProjectProgress().pipe(timeout(10000), catchError(() => of([]))),
      reports: this.api.getReports().pipe(timeout(10000), catchError(() => of([]))),
      notifications: this.api.getNotifications().pipe(timeout(10000), catchError(() => of([]))),
      procurements: this.api.getProcurements().pipe(timeout(10000), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: data => {
        this.analytics = data.analytics || {};
        this.users = Array.isArray(data.users) ? data.users : [];
        this.reports = Array.isArray(data.reports) ? data.reports : [];

        const progressRows = Array.isArray(data.progress) ? data.progress : [];
        const progressMap = new Map<number, number>(
          progressRows.map((row: any) => [Number(row.project_id), this.pct(row.progress)])
        );

        this.projects = (Array.isArray(data.projects) ? data.projects : []).map((project: any) => ({
          id: Number(project.id),
          project_name: project.project_name || project.name || 'Unnamed project',
          status: project.status || 'Planning',
          location: project.location || '',
          manager_id: project.manager_id ?? project.project_manager_id ?? null,
          progress: progressMap.get(Number(project.id)) ?? this.pct(project.progress)
        }));

        this.summary = {
          users: this.users.length,
          projects: this.projects.length,
          activeProjects: this.projects.filter(p => p.status === 'In Progress').length,
          completedProjects: this.projects.filter(p => p.status === 'Completed' || p.status === 'Closed').length,
          workers: Number(this.analytics?.workers?.total ?? 0),
          resources: Number(this.analytics?.resources?.total ?? 0),
          procurements: Number(this.analytics?.procurements?.total ?? (Array.isArray(data.procurements) ? data.procurements.length : 0)),
          reports: this.reports.length
        };

        const roleMap = new Map<string, number>();
        this.users.forEach(user => {
          const role = String(user.role || 'UNKNOWN').toUpperCase();
          roleMap.set(role, (roleMap.get(role) || 0) + 1);
        });
        this.roleCounts = [...roleMap.entries()].map(([role, count]) => ({ role, count })).sort((a, b) => b.count - a.count);

        const notifications = Array.isArray(data.notifications) ? data.notifications : [];
        const procurements = Array.isArray(data.procurements) ? data.procurements : [];
        this.activities = [
          ...notifications.map((x: any) => ({ type: 'Notification', title: x.title || x.message || 'System notification', status: x.status || (x.is_read ? 'Read' : 'Unread'), time: x.created_at || x.createdAt || '' })),
          ...procurements.map((x: any) => ({ type: 'Procurement', title: x.item_name || x.title || x.vendor_name || 'Procurement activity', status: x.status || 'Pending', time: x.created_at || x.createdAt || '' })),
          ...this.reports.map((x: any) => ({ type: 'Report', title: x.title || 'Report', status: x.status || 'Draft', time: x.created_at || x.createdAt || '' }))
        ].sort((a, b) => this.timeValue(b.time) - this.timeValue(a.time)).slice(0, 8);
      },
      error: () => {
        this.error = 'Unable to load the administrator dashboard. Check that the backend is running.';
      }
    });
  }

  pct(value: any): number { return Math.max(0, Math.min(100, Number(value) || 0)); }
  private timeValue(value: any): number { const t = value ? new Date(value).getTime() : 0; return Number.isFinite(t) ? t : 0; }
  roleLabel(role: string): string { return role.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()); }
}
