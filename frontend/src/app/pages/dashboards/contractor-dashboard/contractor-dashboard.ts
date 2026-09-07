import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { catchError, filter, finalize, forkJoin, of, Subject, takeUntil, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-contractor-dashboard',
  standalone: true,
  imports: [CommonModule, AppSidebarComponent],
  templateUrl: './contractor-dashboard.html',
  styleUrl: './contractor-dashboard.css'
})
export class ContractorDashboard implements OnInit, OnDestroy {
  projects: any[] = [];
  assignments: any[] = [];
  attendance: any[] = [];
  loading = true;
  error = '';

  private readonly destroy$ = new Subject<void>();
  private readonly focusHandler = () => this.load(false);

  constructor(private api: Api, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit(): void {
    this.load();
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      filter(event => event.urlAfterRedirects.includes('/contractor-dashboard')),
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
      assignments: this.api.getWorkerAssignments().pipe(timeout(10000), catchError(() => of([]))),
      attendance: this.api.getAttendance().pipe(timeout(10000), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: data => {
        this.projects = Array.isArray(data.projects) ? data.projects : [];
        this.assignments = Array.isArray(data.assignments) ? data.assignments : [];
        this.attendance = Array.isArray(data.attendance) ? data.attendance : [];
      },
      error: e => {
        this.error = e?.error?.detail || 'Unable to load contractor overview. Check that the backend is running.';
      }
    });
  }

  get activeCount(): number { return this.projects.filter(p => p.status === 'In Progress').length; }
  get completedCount(): number { return this.projects.filter(p => p.status === 'Completed' || p.status === 'Closed').length; }
  get assignmentCount(): number { return this.assignments.length; }
  get todayAttendanceCount(): number {
    const today = new Date().toISOString().slice(0, 10);
    return this.attendance.filter(a => String(a.date || '').slice(0, 10) === today).length;
  }
  statusClass(status: string): string { return String(status || '').toLowerCase().replace(/\s+/g, '-'); }
}
