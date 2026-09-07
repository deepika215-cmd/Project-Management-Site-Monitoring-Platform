import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { catchError, filter, finalize, forkJoin, of, Subject, takeUntil, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-worker-dashboard',
  standalone: true,
  imports: [CommonModule, AppSidebarComponent],
  templateUrl: './worker-dashboard.html',
  styleUrl: './worker-dashboard.css'
})
export class WorkerDashboard implements OnInit, OnDestroy {
  currentUser: any = null;
  worker: any = null;
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
      filter(event => event.urlAfterRedirects.includes('/worker-dashboard')),
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
      user: this.api.getCurrentUser().pipe(timeout(10000), catchError(() => of(null))),
      workers: this.api.getWorkers().pipe(timeout(10000), catchError(() => of([]))),
      attendance: this.api.getAttendance().pipe(timeout(10000), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: ({ user, workers, attendance }) => {
        this.currentUser = user;
        const rows = Array.isArray(workers) ? workers : [];
        this.worker = rows.find((w: any) => String(w.email || '').toLowerCase() === String(user?.email || '').toLowerCase()) || rows[0] || null;
        this.attendance = (Array.isArray(attendance) ? attendance : []).filter((a: any) => !this.worker || Number(a.worker_id) === Number(this.worker.id));
      },
      error: err => {
        this.error = err?.error?.detail || 'Unable to load worker data. Check that the backend is running.';
      }
    });
  }

  get presentCount(): number { return this.attendance.filter(a => String(a.status || '').toLowerCase() === 'present').length; }
  get absentCount(): number { return this.attendance.filter(a => String(a.status || '').toLowerCase() === 'absent').length; }
  get attendanceRate(): number {
    const total = this.presentCount + this.absentCount;
    return total ? Math.round(this.presentCount / total * 100) : 0;
  }
}
