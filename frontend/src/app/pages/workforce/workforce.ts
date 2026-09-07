import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

interface Worker {
  id: number;
  name: string;
  role: string;
  phone: string;
  email: string;
  status?: string;
  is_active?: boolean;
  category?: string;
  skill_type?: string;
  contractor_id?: number | null;
  joining_date?: string | null;
}

interface BulkWorkerResult {
  message?: string;
  total_rows?: number;
  successful?: number;
  created?: number;
  failed?: number;
  skipped?: number;
  created_workers?: Worker[];
  failed_rows?: Array<{ row: number; name?: string; error: string }>;
  skipped_rows?: Array<{ row: number; name?: string; reason: string; worker_id?: number }>;
}

@Component({
  selector: 'app-workforce',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './workforce.html',
  styleUrl: './workforce.css'
})
export class Workforce implements OnInit {
  workers: Worker[] = [];
  attendance: any[] = [];

  search = '';
  loading = false;
  error = '';
  success = '';
  showForm = false;
  showBulk = false;
  saving = false;
  bulkUploading = false;
  actionWorkerId: number | null = null;

  bulkFile: File | null = null;
  bulkResult: BulkWorkerResult | null = null;

  form = this.emptyForm();

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';

    forkJoin({
      workers: this.api.getWorkers().pipe(timeout(9000), catchError(error => {
        this.error = this.readError(error, 'Unable to load workers from the backend.');
        return of([] as Worker[]);
      })),
      attendance: this.api.getAttendance().pipe(timeout(9000), catchError(() => of([] as any[])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe(({ workers, attendance }) => {
      this.workers = Array.isArray(workers) ? workers : [];
      this.attendance = Array.isArray(attendance) ? attendance : [];
    });
  }

  get filteredWorkers(): Worker[] {
    const term = this.search.trim().toLowerCase();
    if (!term) return this.workers;
    return this.workers.filter(worker =>
      String(worker.name || '').toLowerCase().includes(term) ||
      String(worker.role || '').toLowerCase().includes(term) ||
      String(worker.email || '').toLowerCase().includes(term) ||
      String(worker.phone || '').toLowerCase().includes(term) ||
      String(worker.category || '').toLowerCase().includes(term) ||
      String(worker.skill_type || '').toLowerCase().includes(term)
    );
  }

  activeCount(): number {
    return this.workers.filter(worker =>
      worker.is_active === true || String(worker.status || '').toLowerCase() === 'active'
    ).length;
  }

  inactiveCount(): number {
    return Math.max(this.workers.length - this.activeCount(), 0);
  }

  attendanceCount(workerId: number): number {
    return this.attendance.filter(record => Number(record?.worker_id) === Number(workerId)).length;
  }

  openForm(): void {
    this.form = this.emptyForm();
    this.error = '';
    this.success = '';
    this.showForm = true;
    this.showBulk = false;
  }

  cancelForm(): void {
    this.showForm = false;
    this.saving = false;
  }

  openBulk(): void {
    this.error = '';
    this.success = '';
    this.bulkResult = null;
    this.bulkFile = null;
    this.showBulk = true;
    this.showForm = false;
  }

  cancelBulk(): void {
    this.showBulk = false;
    this.bulkUploading = false;
    this.bulkFile = null;
    this.bulkResult = null;
  }

  onBulkFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.error = '';
    this.success = '';
    this.bulkResult = null;
    this.bulkFile = input.files && input.files.length ? input.files[0] : null;

    if (!this.bulkFile) return;

    const fileName = this.bulkFile.name.toLowerCase();
    if (!fileName.endsWith('.csv') && !fileName.endsWith('.xlsx')) {
      this.error = 'Please choose a CSV or XLSX file.';
      this.bulkFile = null;
      input.value = '';
      return;
    }

    if (this.bulkFile.size > 5 * 1024 * 1024) {
      this.error = 'Bulk worker file must be below 5 MB.';
      this.bulkFile = null;
      input.value = '';
    }
  }

  uploadBulkWorkers(): void {
    if (!this.bulkFile) {
      this.error = 'Please select a CSV or XLSX file before uploading.';
      return;
    }

    this.bulkUploading = true;
    this.error = '';
    this.success = '';
    this.bulkResult = null;

    this.api.bulkCreateWorkers(this.bulkFile).pipe(
      timeout(20000),
      finalize(() => {
        this.bulkUploading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (result: BulkWorkerResult) => {
        this.bulkResult = result;
        const created = Number(result.successful ?? result.created ?? 0);
        const failed = Number(result.failed ?? 0);
        const skipped = Number(result.skipped ?? 0);

        if (Array.isArray(result.created_workers) && result.created_workers.length) {
          const createdIds = new Set(result.created_workers.map(worker => Number(worker.id)));
          this.workers = [
            ...result.created_workers,
            ...this.workers.filter(worker => !createdIds.has(Number(worker.id)))
          ];
        }

        this.success = `Bulk upload completed: ${created} created, ${skipped} skipped, ${failed} failed.`;
        this.load();
      },
      error: error => {
        this.error = this.readError(error, 'Unable to upload bulk workers. Check file format and backend terminal.');
      }
    });
  }

  downloadWorkerTemplate(): void {
    const rows = [
      ['name', 'role', 'phone', 'email', 'category', 'skill_type', 'contractor_id', 'joining_date', 'status'],
      ['Ravi Kumar', 'Mason', '9876543210', 'ravi.worker@buildtrack.com', 'Skilled Worker', 'Brick Work', '', '2026-09-01', 'Active'],
      ['Suresh Kumar', 'Electrician', '9876543211', 'suresh.worker@buildtrack.com', 'Skilled Worker', 'Electrical Wiring', '', '2026-09-02', 'Active'],
      ['Meena Devi', 'Site Helper', '9876543212', 'meena.worker@buildtrack.com', 'Unskilled Worker', 'Material Handling', '', '2026-09-03', 'Active']
    ];

    const csv = rows
      .map(row => row.map(value => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'buildtrack_workers_bulk_template.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  }

  add(): void {
    if (!this.form.name.trim() || !this.form.email.trim() || !this.form.phone.trim()) {
      this.error = 'Name, email and phone are required.';
      return;
    }

    this.saving = true;
    this.error = '';
    this.success = '';

    const payload = {
      name: this.form.name.trim(),
      role: this.form.role.trim() || 'Worker',
      phone: this.form.phone.trim(),
      email: this.form.email.trim(),
      status: this.form.status || 'Active',
      category: 'Skilled Worker'
    };

    this.api.createWorker(payload).pipe(
      timeout(10000),
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (created: any) => {
        if (created?.id) {
          this.workers = [created, ...this.workers.filter(worker => Number(worker.id) !== Number(created.id))];
        }
        this.success = 'Worker registered successfully.';
        this.showForm = false;
        this.form = this.emptyForm();
        this.load();
      },
      error: error => {
        this.error = this.readError(error, 'Unable to create worker. Check the backend terminal for details.');
      }
    });
  }

  remove(worker: Worker): void {
    if (!worker?.id || !confirm(`Delete ${worker.name}? This action cannot be undone.`)) return;

    this.error = '';
    this.success = '';
    this.actionWorkerId = worker.id;

    this.api.deleteWorker(worker.id).pipe(
      timeout(10000),
      finalize(() => {
        this.actionWorkerId = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.workers = this.workers.filter(item => item.id !== worker.id);
        this.success = 'Worker deleted successfully.';
      },
      error: error => {
        this.error = this.readError(error, 'Unable to delete worker. Only Admin users can delete workers.');
      }
    });
  }

  mark(worker: Worker, status: string): void {
    if (!worker?.id) return;

    this.error = '';
    this.success = '';
    this.actionWorkerId = worker.id;

    this.api.createAttendance({
      worker_id: worker.id,
      date: new Date().toISOString().slice(0, 10),
      status
    }).pipe(
      timeout(10000),
      finalize(() => {
        this.actionWorkerId = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (record: any) => {
        if (record?.id) this.attendance = [record, ...this.attendance];
        this.success = `${status} attendance recorded for ${worker.name}.`;
        this.load();
      },
      error: error => {
        this.error = this.readError(error, 'Unable to record attendance.');
      }
    });
  }

  statusLabel(worker: Worker): string {
    if (worker.is_active === true) return 'Active';
    if (worker.is_active === false) return 'Inactive';
    return worker.status || 'Active';
  }

  statusClass(worker: Worker): string {
    return this.statusLabel(worker).toLowerCase() === 'active' ? 'status-active' : 'status-inactive';
  }

  private emptyForm() {
    return { name: '', role: 'Worker', phone: '', email: '', status: 'Active' };
  }

  private readError(error: any, fallback: string): string {
    const detail = error?.error?.detail ?? error?.error?.message ?? error?.message;
    if (Array.isArray(detail)) return detail.map((item: any) => item?.msg || item?.message || String(item)).join(', ');
    return detail || fallback;
  }
}
