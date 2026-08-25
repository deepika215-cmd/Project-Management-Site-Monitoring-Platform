import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
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
  showForm = false;
  saving = false;

  form = {
    name: '',
    role: 'Worker',
    phone: '',
    email: '',
    status: 'Active'
  };

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.error = '';

    this.api.getWorkers().subscribe({
      next: (workers: any) => {
        this.workers = Array.isArray(workers)
          ? workers
          : Array.isArray(workers?.workers)
            ? workers.workers
            : Array.isArray(workers?.data)
              ? workers.data
              : [];

        this.api.getAttendance().subscribe({
          next: (records: any) => {
            this.attendance = Array.isArray(records)
              ? records
              : Array.isArray(records?.attendance)
                ? records.attendance
                : Array.isArray(records?.data)
                  ? records.data
                  : [];
            this.loading = false;
          },
          error: () => {
            // Workforce data should still be usable if attendance fails.
            this.attendance = [];
            this.loading = false;
          }
        });
      },
      error: (error: any) => {
        this.workers = [];
        this.attendance = [];
        this.loading = false;
        this.error =
          error?.error?.detail ||
          error?.error?.message ||
          'Unable to load workforce data from the backend.';
      }
    });
  }

  get filteredWorkers(): Worker[] {
    const term = this.search.trim().toLowerCase();

    if (!term) {
      return this.workers;
    }

    return this.workers.filter(worker =>
      String(worker.name || '').toLowerCase().includes(term) ||
      String(worker.role || '').toLowerCase().includes(term) ||
      String(worker.email || '').toLowerCase().includes(term) ||
      String(worker.phone || '').toLowerCase().includes(term)
    );
  }

  activeCount(): number {
    return this.workers.filter(worker =>
      worker.is_active === true ||
      String(worker.status || '').toLowerCase() === 'active'
    ).length;
  }

  inactiveCount(): number {
    return Math.max(this.workers.length - this.activeCount(), 0);
  }

  attendanceCount(workerId: number): number {
    return this.attendance.filter(record =>
      Number(record?.worker_id) === Number(workerId)
    ).length;
  }

  openForm(): void {
    this.form = {
      name: '',
      role: 'Worker',
      phone: '',
      email: '',
      status: 'Active'
    };
    this.error = '';
    this.showForm = true;
  }

  cancelForm(): void {
    this.showForm = false;
    this.saving = false;
  }

  add(): void {
    if (!this.form.name.trim() || !this.form.email.trim() || !this.form.phone.trim()) {
      this.error = 'Name, email and phone are required.';
      return;
    }

    this.saving = true;
    this.error = '';

    this.api.createWorker({
      name: this.form.name.trim(),
      role: this.form.role.trim(),
      phone: this.form.phone.trim(),
      email: this.form.email.trim(),
      status: this.form.status
    }).subscribe({
      next: () => {
        this.saving = false;
        this.showForm = false;
        this.load();
      },
      error: (error: any) => {
        this.saving = false;
        this.error =
          error?.error?.detail ||
          error?.error?.message ||
          'Unable to create worker.';
      }
    });
  }

  remove(worker: Worker): void {
    if (!confirm(`Delete ${worker.name}? This action cannot be undone.`)) {
      return;
    }

    this.api.deleteWorker(worker.id).subscribe({
      next: () => {
        this.workers = this.workers.filter(item => item.id !== worker.id);
      },
      error: (error: any) => {
        this.error =
          error?.error?.detail ||
          error?.error?.message ||
          'Unable to delete worker.';
      }
    });
  }

  mark(worker: Worker, status: string): void {
    this.error = '';

    this.api.createAttendance({
      worker_id: worker.id,
      date: new Date().toISOString().slice(0, 10),
      status
    }).subscribe({
      next: () => this.load(),
      error: (error: any) => {
        this.error =
          error?.error?.detail ||
          error?.error?.message ||
          'Unable to record attendance.';
      }
    });
  }

  statusLabel(worker: Worker): string {
    if (worker.is_active === true) return 'Active';
    if (worker.is_active === false) return 'Inactive';
    return worker.status || 'Active';
  }

  statusClass(worker: Worker): string {
    return this.statusLabel(worker).toLowerCase() === 'active'
      ? 'status-active'
      : 'status-inactive';
  }
}
