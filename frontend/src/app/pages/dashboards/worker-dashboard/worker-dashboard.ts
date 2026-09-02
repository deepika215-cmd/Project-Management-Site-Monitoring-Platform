import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({ selector: 'app-worker-dashboard', standalone: true, imports: [CommonModule, RouterLink, AppSidebarComponent], templateUrl: './worker-dashboard.html', styleUrl: './worker-dashboard.css' })
export class WorkerDashboard implements OnInit {
  currentUser: any = null; worker: any = null; attendance: any[] = []; loading = true; error = '';

  constructor(private api: Api) {}

  ngOnInit(): void {
    forkJoin({ user: this.api.getCurrentUser(), workers: this.api.getWorkers(), attendance: this.api.getAttendance() }).subscribe({
      next: ({ user, workers, attendance }) => {
        this.currentUser = user;
        const rows = Array.isArray(workers) ? workers : [];
        this.worker = rows.find((w: any) => String(w.email || '').toLowerCase() === String(user?.email || '').toLowerCase()) || null;
        this.attendance = (Array.isArray(attendance) ? attendance : []).filter((a: any) => !this.worker || Number(a.worker_id) === Number(this.worker.id));
        this.loading = false;
      },
      error: err => { this.loading = false; this.error = err?.error?.detail || 'Unable to load worker data.'; }
    });
  }

  get presentCount(): number { return this.attendance.filter(a => String(a.status || '').toLowerCase() === 'present').length; }
  get absentCount(): number { return this.attendance.filter(a => String(a.status || '').toLowerCase() === 'absent').length; }
  get attendanceRate(): number { const total = this.presentCount + this.absentCount; return total ? Math.round(this.presentCount / total * 100) : 0; }
}
