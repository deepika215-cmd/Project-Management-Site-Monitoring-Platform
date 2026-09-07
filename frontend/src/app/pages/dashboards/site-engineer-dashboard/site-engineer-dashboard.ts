import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router, RouterLink } from '@angular/router';
import { catchError, filter, finalize, forkJoin, of, Subject, takeUntil, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-site-engineer-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, AppSidebarComponent],
  templateUrl: './site-engineer-dashboard.html',
  styleUrl: './site-engineer-dashboard.css'
})
export class SiteEngineerDashboard implements OnInit, OnDestroy {
  projects: any[] = [];
  progress: any[] = [];
  resources: any[] = [];
  loading = true;
  error = '';

  private readonly destroy$ = new Subject<void>();
  private readonly focusHandler = () => this.load(false);

  constructor(private api: Api, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit(): void {
    this.load();
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      filter(event => event.urlAfterRedirects.includes('/site-engineer-dashboard')),
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
      progress: this.api.getProjectProgress().pipe(timeout(10000), catchError(() => of([]))),
      resources: this.api.getResourceUtilizationAnalytics().pipe(timeout(10000), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: data => {
        this.projects = Array.isArray(data.projects) ? data.projects : [];
        this.progress = Array.isArray(data.progress) ? data.progress : [];
        this.resources = Array.isArray(data.resources) ? data.resources : [];
      },
      error: err => {
        this.error = err?.error?.detail || 'Unable to load site monitoring data. Check that the backend is running.';
      }
    });
  }

  progressFor(id: number): number { return Number(this.progress.find(p => Number(p.project_id) === Number(id))?.progress || 0); }
  resourceUtilization(): number {
    const rows = this.resources;
    const total = rows.reduce((s, r) => s + Number(r.total_quantity ?? r.quantity ?? 0), 0);
    const allocated = rows.reduce((s, r) => s + Number(r.allocated_quantity ?? r.allocated ?? 0), 0);
    return total ? Math.round(allocated / total * 100) : 0;
  }
}
