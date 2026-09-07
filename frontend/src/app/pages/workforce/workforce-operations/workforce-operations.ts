import { CommonModule } from '@angular/common';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-workforce-operations',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './workforce-operations.html',
  styleUrl: './workforce-operations.css'
})
export class WorkforceOperations implements OnInit {
  tab: 'assignments'|'shifts'|'payroll' = 'assignments';
  workers: any[] = [];
  projects: any[] = [];
  contractors: any[] = [];
  assignments: any[] = [];
  shifts: any[] = [];
  payroll: any[] = [];
  loading = false;
  saving = false;
  error = '';
  message = '';
  role = '';
  today = new Date().toISOString().slice(0,10);
  assignment: any = this.emptyAssignment();
  shift: any = this.emptyShift();
  pay: any = this.emptyPay();

  constructor(private api: Api, private cdr: ChangeDetectorRef) {
    try { this.role = String(JSON.parse(localStorage.getItem('currentUser') || '{}').role || '').toUpperCase(); } catch {}
  }

  ngOnInit(): void { this.load(); }
  canPayroll(): boolean { return this.role === 'ADMIN' || this.role === 'PROJECT_MANAGER'; }

  load(): void {
    this.loading = true;
    this.error = '';
    forkJoin({
      workers: this.api.getWorkers().pipe(timeout(9000), catchError(() => of([] as any[]))),
      projects: this.api.getProjects().pipe(timeout(9000), catchError(() => of([] as any[]))),
      contractors: this.api.getContractors().pipe(timeout(9000), catchError(() => of([] as any[]))),
      assignments: this.api.getWorkerAssignments().pipe(timeout(9000), catchError(() => of([] as any[]))),
      shifts: this.api.getShifts().pipe(timeout(9000), catchError(() => of([] as any[]))),
      payroll: this.canPayroll() ? this.api.getPayroll().pipe(timeout(9000), catchError(() => of([] as any[]))) : of([] as any[])
    }).pipe(finalize(() => { this.loading = false; this.cdr.detectChanges(); }))
      .subscribe(r => {
        this.workers = r.workers || [];
        this.projects = r.projects || [];
        this.contractors = r.contractors || [];
        this.assignments = r.assignments || [];
        this.shifts = r.shifts || [];
        this.payroll = r.payroll || [];
        this.setDefaults();
      });
  }

  workerName(id: any): string { return this.workers.find(w => Number(w.id) === Number(id))?.name || `Worker #${id}`; }
  projectName(id: any): string { return this.projects.find(p => Number(p.id) === Number(id))?.project_name || `Project #${id}`; }
  contractorName(id: any): string { return this.contractors.find(c => Number(c.id) === Number(id))?.name || `Contractor #${id}`; }

  addAssignment(): void {
    if (!this.assignment.worker_id || !this.assignment.project_id || !this.assignment.contractor_id || !this.assignment.activity.trim()) {
      this.error = 'Worker, project, contractor and activity are required.';
      return;
    }
    this.saving = true;
    this.error = '';
    this.message = '';
    const payload = {
      worker_id: Number(this.assignment.worker_id),
      contractor_id: Number(this.assignment.contractor_id),
      project_id: Number(this.assignment.project_id),
      work_activity: this.assignment.activity.trim(),
      assignment_start_date: this.assignment.start_date,
      assignment_end_date: this.assignment.end_date || null,
      assignment_status: String(this.assignment.status || 'ACTIVE').toUpperCase()
    };
    this.api.createWorkerAssignment(payload).pipe(timeout(10000), finalize(() => { this.saving = false; this.cdr.detectChanges(); }))
      .subscribe({
        next: (created: any) => {
          if (created?.id) this.assignments = [created, ...this.assignments];
          this.message = 'Worker assigned successfully.';
          this.assignment = { ...this.emptyAssignment(), worker_id: this.assignment.worker_id, project_id: this.assignment.project_id, contractor_id: this.assignment.contractor_id };
          this.load();
        },
        error: e => this.error = this.detail(e, 'Unable to assign worker.')
      });
  }

  addShift(): void {
    if (!this.shift.worker_id || !this.shift.project_id || !this.shift.shift_name.trim()) {
      this.error = 'Shift name, worker and project are required.';
      return;
    }
    this.saving = true;
    this.error = '';
    this.message = '';
    this.api.createShift({ ...this.shift, status: String(this.shift.status || 'SCHEDULED').toUpperCase() })
      .pipe(timeout(10000), finalize(() => { this.saving = false; this.cdr.detectChanges(); }))
      .subscribe({
        next: (created: any) => { if (created?.id) this.shifts = [created, ...this.shifts]; this.message = 'Shift scheduled.'; this.load(); },
        error: e => this.error = this.detail(e, 'Unable to schedule shift.')
      });
  }

  addPayroll(): void {
    if (!this.canPayroll()) return;
    if (!this.pay.worker_id || Number(this.pay.pay_rate) < 0) {
      this.error = 'Worker and valid pay rate are required.';
      return;
    }
    this.saving = true;
    this.error = '';
    this.message = '';
    const payload = {
      worker_id: Number(this.pay.worker_id),
      project_id: this.pay.project_id ? Number(this.pay.project_id) : null,
      pay_rate: Number(this.pay.pay_rate || 0),
      working_days: Number(this.pay.working_days || 0),
      working_hours: Number(this.pay.working_hours || 0),
      overtime_hours: Number(this.pay.overtime_hours || 0),
      leave_days: Number(this.pay.leave_days || 0),
      payroll_status: String(this.pay.status || 'PENDING').toUpperCase()
    };
    this.api.createPayroll(payload).pipe(timeout(10000), finalize(() => { this.saving = false; this.cdr.detectChanges(); }))
      .subscribe({
        next: (created: any) => { if (created?.id) this.payroll = [created, ...this.payroll]; this.message = 'Payroll estimate created.'; this.load(); },
        error: e => this.error = this.detail(e, 'Unable to save payroll.')
      });
  }

  removeAssignment(id: number): void {
    if (!confirm('Delete this assignment record?')) return;
    this.api.deleteWorkerAssignment(id).pipe(timeout(10000)).subscribe({
      next: () => { this.assignments = this.assignments.filter(a => Number(a.id) !== Number(id)); this.message = 'Assignment deleted.'; },
      error: e => this.error = this.detail(e, 'Unable to delete assignment.')
    });
  }

  removeShift(id: number): void {
    if (!confirm('Delete this shift?')) return;
    this.api.deleteShift(id).pipe(timeout(10000)).subscribe({
      next: () => { this.shifts = this.shifts.filter(s => Number(s.id) !== Number(id)); this.message = 'Shift deleted.'; },
      error: e => this.error = this.detail(e, 'Unable to delete shift.')
    });
  }

  removePayroll(id: number): void {
    if (!confirm('Delete this payroll record?')) return;
    this.api.deletePayroll(id).pipe(timeout(10000)).subscribe({
      next: () => { this.payroll = this.payroll.filter(p => Number(p.id) !== Number(id)); this.message = 'Payroll record deleted.'; },
      error: e => this.error = this.detail(e, 'Unable to delete payroll.')
    });
  }

  private setDefaults(): void {
    const w = Number(this.workers[0]?.id || 0);
    const p = Number(this.projects[0]?.id || 0);
    const c = Number(this.contractors[0]?.id || 0);
    this.assignment.worker_id ||= w;
    this.assignment.project_id ||= p;
    this.assignment.contractor_id ||= c;
    this.shift.worker_id ||= w;
    this.shift.project_id ||= p;
    this.pay.worker_id ||= w;
    this.pay.project_id ||= p;
  }

  private emptyAssignment(): any { return { worker_id: 0, project_id: 0, contractor_id: 0, activity: '', start_date: this.today, end_date: null, status: 'ACTIVE' }; }
  private emptyShift(): any { return { shift_name: 'Day Shift', worker_id: 0, project_id: 0, shift_date: this.today, start_time: '08:00', end_time: '17:00', status: 'SCHEDULED' }; }
  private emptyPay(): any { return { worker_id: 0, project_id: 0, pay_rate: 0, working_days: 0, working_hours: 0, overtime_hours: 0, leave_days: 0, status: 'PENDING' }; }
  private detail(e: any, fallback: string): string {
    const d = e?.error?.detail ?? e?.error?.message ?? e?.message;
    return Array.isArray(d) ? d.map((x: any) => x?.msg || String(x)).join(', ') : d || fallback;
  }
}
