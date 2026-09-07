import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-attendance',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './attendance.html',
  styleUrl: './attendance.css'
})
export class Attendance implements OnInit {
  records: any[] = [];
  filteredRecords: any[] = [];
  workers: any[] = [];
  loading = false;
  saving = false;
  error = '';
  success = '';
  editingId: number | null = null;
  currentUser: any = {};
  role = '';
  workerRecord: any = null;

  filterWorkerId = 0;
  filterStatus = '';
  filterDate = '';

  form = this.emptyForm();

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    try { this.currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}'); } catch { this.currentUser = {}; }
    this.role = String(this.currentUser?.role || '').toUpperCase();
    this.load();
  }

  get canManage(): boolean {
    return ['ADMIN', 'PROJECT_MANAGER', 'CONTRACTOR'].includes(this.role);
  }

  get isWorker(): boolean { return this.role === 'WORKER'; }

  load(): void {
    this.loading = true;
    this.error = '';

    forkJoin({
      workers: this.api.getWorkers().pipe(timeout(9000), catchError(() => of([] as any[]))),
      attendance: this.api.getAttendance().pipe(timeout(9000), catchError(err => {
        this.error = this.readError(err, 'Unable to load attendance data.');
        return of([] as any[]);
      }))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe(({ workers, attendance }) => {
      this.workers = Array.isArray(workers) ? workers : [];
      const allRecords = Array.isArray(attendance) ? attendance : [];

      if (this.isWorker) {
        const email = String(this.currentUser?.email || '').toLowerCase();
        this.workerRecord = this.workers.find(w => String(w?.email || '').toLowerCase() === email) || null;
        this.records = this.workerRecord ? allRecords.filter(r => Number(r.worker_id) === Number(this.workerRecord.id)) : allRecords;
      } else {
        this.records = allRecords;
      }

      this.applyFilters();
    });
  }

  save(): void {
    this.error = '';
    this.success = '';
    if (!this.canManage) return;
    if (!this.form.worker_id || !this.form.date || !this.form.status) {
      this.error = 'Please select a worker, date and attendance status.';
      return;
    }

    this.saving = true;
    const payload = { ...this.form };
    const request = this.editingId ? this.api.updateAttendance(this.editingId, payload) : this.api.createAttendance(payload);

    request.pipe(
      timeout(10000),
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (record: any) => {
        this.success = this.editingId ? 'Attendance updated successfully.' : 'Attendance recorded successfully.';
        if (record?.id) {
          this.records = [record, ...this.records.filter(item => Number(item.id) !== Number(record.id))];
          this.applyFilters();
        }
        this.cancelEdit();
        this.load();
      },
      error: err => {
        this.error = this.readError(err, 'Unable to save attendance.');
      }
    });
  }

  edit(record: any): void {
    if (!this.canManage) return;
    this.editingId = Number(record.id);
    this.form = { worker_id: Number(record.worker_id), date: String(record.date), status: String(record.status) };
    this.error = '';
    this.success = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelEdit(): void {
    this.editingId = null;
    this.form = this.emptyForm();
  }

  remove(record: any): void {
    if (!this.canManage || !record?.id) return;
    const name = this.workerName(record.worker_id);
    if (!confirm(`Delete attendance for ${name} on ${record.date}?`)) return;
    this.error = '';
    this.success = '';
    this.api.deleteAttendance(Number(record.id)).pipe(timeout(10000)).subscribe({
      next: () => {
        this.records = this.records.filter(item => Number(item.id) !== Number(record.id));
        this.applyFilters();
        this.success = 'Attendance deleted successfully.';
      },
      error: err => { this.error = this.readError(err, 'Unable to delete attendance.'); }
    });
  }

  applyFilters(): void {
    this.filteredRecords = this.records.filter(record =>
      (!this.filterWorkerId || Number(record.worker_id) === Number(this.filterWorkerId)) &&
      (!this.filterStatus || record.status === this.filterStatus) &&
      (!this.filterDate || record.date === this.filterDate)
    );
  }

  clearFilters(): void {
    this.filterWorkerId = 0;
    this.filterStatus = '';
    this.filterDate = '';
    this.applyFilters();
  }

  workerName(workerId: number): string {
    const worker = this.workers.find(w => Number(w.id) === Number(workerId));
    return worker?.name || `Worker #${workerId}`;
  }

  count(status: string): number { return this.records.filter(r => r.status === status).length; }

  attendanceRate(): number {
    const considered = this.records.filter(r => ['Present', 'Absent', 'Late', 'Half Day'].includes(r.status));
    if (!considered.length) return 0;
    const value = considered.reduce((sum, r) => sum + (r.status === 'Present' ? 1 : r.status === 'Late' ? 1 : r.status === 'Half Day' ? 0.5 : 0), 0);
    return Math.round((value / considered.length) * 100);
  }

  statusClass(status: string): string { return String(status || '').toLowerCase().replace(/\s+/g, '-'); }

  private emptyForm() {
    return { worker_id: 0, date: new Date().toISOString().slice(0, 10), status: 'Present' };
  }

  private readError(error: any, fallback: string): string {
    const detail = error?.error?.detail ?? error?.error?.message ?? error?.message;
    if (Array.isArray(detail)) return detail.map((item: any) => item?.msg || item?.message || String(item)).join(', ');
    return detail || fallback;
  }
}
