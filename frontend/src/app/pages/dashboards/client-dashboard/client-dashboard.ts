import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { catchError, filter, finalize, forkJoin, of, Subject, takeUntil, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-client-dashboard',
  standalone: true,
  imports: [CommonModule, AppSidebarComponent],
  templateUrl: './client-dashboard.html',
  styleUrl: './client-dashboard.css'
})
export class ClientDashboard implements OnInit, OnDestroy {
  projects: any[] = [];
  loading = true;
  error = '';
  totalBudget = 0;
  activeProjects = 0;
  completedProjects = 0;
  averageProgress = 0;

  private readonly destroy$ = new Subject<void>();
  private readonly focusHandler = () => this.load(false);

  constructor(private api: Api, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit(): void {
    this.load();
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      filter(event => event.urlAfterRedirects.includes('/client-dashboard')),
      takeUntil(this.destroy$)
    ).subscribe(() => this.load(false));
    window.addEventListener('focus', this.focusHandler);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    window.removeEventListener('focus', this.focusHandler);
  }

  load(showSpinner = true): void {
    if (showSpinner) {
      this.loading = true;
    }
    this.error = '';
    this.cdr.detectChanges();

    forkJoin({
      projects: this.api.getProjects().pipe(timeout(10000), catchError(() => of([]))),
      progress: this.api.getProjectProgress().pipe(timeout(10000), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: ({ projects, progress }) => {
        const rows = Array.isArray(projects) ? projects : [];
        const progressMap = new Map<number, number>((Array.isArray(progress) ? progress : []).map((p: any) => [Number(p.project_id), Number(p.progress) || 0]));
        this.projects = rows.map((p: any) => ({ ...p, progress: progressMap.get(Number(p.id)) ?? Number(p.progress ?? 0) }));
        this.totalBudget = this.projects.reduce((sum, p) => sum + (Number(p.budget ?? p.estimated_budget ?? p.total_budget) || 0), 0);
        this.activeProjects = this.projects.filter(p => p.status === 'In Progress').length;
        this.completedProjects = this.projects.filter(p => p.status === 'Completed' || p.status === 'Closed').length;
        this.averageProgress = this.projects.length ? Math.round(this.projects.reduce((sum, p) => sum + (Number(p.progress) || 0), 0) / this.projects.length) : 0;
      },
      error: err => {
        this.error = err?.error?.detail || 'Unable to load project data. Check that the backend is running.';
      }
    });
  }

  statusClass(status: string): string { return String(status || '').toLowerCase().replace(/\s+/g, '-'); }
}
