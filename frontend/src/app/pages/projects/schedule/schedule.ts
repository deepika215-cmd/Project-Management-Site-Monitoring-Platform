import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';
import { Api } from '../../../services/api';

interface Activity {
  id: number;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  duration: number;
  dependency: string;
  status: string;
}

@Component({
  selector: 'app-schedule',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './schedule.html',
  styleUrl: './schedule.css'
})
export class Schedule implements OnInit {
  projects: any[] = [];
  selectedProjectId = 0;
  activities: Activity[] = [];
  showModal = false;
  editing = false;
  loadingProjects = false;
  loadingActivities = false;
  saving = false;
  deletingId = 0;
  error = '';
  success = '';

  current: Activity = this.blankActivity();

  constructor(private api: Api, private cdr: ChangeDetectorRef) { }

  ngOnInit(): void {
    this.loadProjects();
  }

  private blankActivity(): Activity {
    return {
      id: 0,
      name: '',
      description: '',
      startDate: '',
      endDate: '',
      duration: 0,
      dependency: '',
      status: 'Not Started'
    };
  }

  private message(error: any, fallback: string): string {
    const detail = error?.error?.detail;
    if (Array.isArray(detail)) {
      return detail.map((item: any) => item?.msg || JSON.stringify(item)).join(', ');
    }
    return detail || error?.error?.message || fallback;
  }

  loadProjects(): void {
    this.loadingProjects = true;
    this.error = '';
    this.api.getProjects().pipe(
      finalize(() => {
        this.loadingProjects = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (response: any) => {
        this.projects = Array.isArray(response) ? response : [];
        if (!this.projects.length) {
          this.selectedProjectId = 0;
          this.activities = [];
          return;
        }

        const stillExists = this.projects.some(p => +p.id === +this.selectedProjectId);
        if (!stillExists) {
          this.selectedProjectId = +this.projects[0].id;
        }
        this.loadActivities();
      },
      error: error => {
        this.projects = [];
        this.activities = [];
        this.error = this.message(error, 'Unable to load projects.');
      }
    });
  }

  onProjectChange(): void {
    this.error = '';
    this.success = '';
    if (!this.selectedProjectId) {
      this.activities = [];
      return;
    }
    this.loadActivities();
  }

  loadActivities(): void {
    if (!this.selectedProjectId) {
      this.activities = [];
      return;
    }

    this.loadingActivities = true;
    this.error = '';
    this.api.getProjectSchedule(this.selectedProjectId).pipe(
      finalize(() => {
        this.loadingActivities = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (response: any) => {
        const rows = Array.isArray(response) ? response : [];
        this.activities = rows.map((row: any) => ({
          id: +row.id,
          name: row.activity_name ?? row.name ?? '',
          description: row.description ?? '',
          startDate: row.start_date ?? row.startDate ?? '',
          endDate: row.end_date ?? row.endDate ?? '',
          duration: +(row.duration_days ?? row.duration ?? 0),
          dependency: row.dependency ?? '',
          status: row.status ?? 'Not Started'
        }));
      },
      error: error => {
        this.activities = [];
        this.error = this.message(error, 'Unable to load this project schedule.');
      }
    });
  }

  get project(): any {
    return this.projects.find(p => +p.id === +this.selectedProjectId);
  }

  get completed(): number {
    return this.activities.filter(a => a.status === 'Completed').length;
  }

  get delayed(): number {
    return this.activities.filter(a => a.status === 'Delayed').length;
  }

  get progress(): number {
    return this.activities.length ? Math.round(this.completed / this.activities.length * 100) : 0;
  }

  openAdd(): void {
    if (!this.selectedProjectId) {
      this.error = 'Select a project before adding an activity.';
      return;
    }
    this.editing = false;
    this.current = this.blankActivity();
    this.error = '';
    this.success = '';
    this.showModal = true;
  }

  edit(activity: Activity): void {
    this.editing = true;
    this.current = { ...activity };
    this.error = '';
    this.success = '';
    this.showModal = true;
  }

  duration(): void {
    if (!this.current.startDate || !this.current.endDate) {
      this.current.duration = 0;
      return;
    }
    const start = new Date(`${this.current.startDate}T00:00:00`).getTime();
    const end = new Date(`${this.current.endDate}T00:00:00`).getTime();
    this.current.duration = end >= start ? Math.floor((end - start) / 86400000) + 1 : 0;
  }

  save(): void {
    this.duration();
    this.error = '';
    this.success = '';

    if (!this.selectedProjectId) {
      this.error = 'Select a project first.';
      return;
    }
    if (!this.current.name.trim() || !this.current.startDate || !this.current.endDate) {
      this.error = 'Activity name, start date and end date are required.';
      return;
    }
    if (this.current.duration <= 0) {
      this.error = 'End date cannot be before start date.';
      return;
    }

    const payload: any = {
      activity_name: this.current.name.trim(),
      description: this.current.description.trim() || null,
      start_date: this.current.startDate,
      end_date: this.current.endDate,
      dependency: this.current.dependency || null,
      status: this.current.status
    };

    const request = this.editing
      ? this.api.updateProjectScheduleActivity(this.current.id, payload)
      : this.api.createProjectScheduleActivity({ ...payload, project_id: this.selectedProjectId });

    this.saving = true;
    request.pipe(
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (row: any) => {
        const saved: Activity = {
          id: +row.id,
          name: row.activity_name ?? '',
          description: row.description ?? '',
          startDate: row.start_date ?? '',
          endDate: row.end_date ?? '',
          duration: +(row.duration_days ?? 0),
          dependency: row.dependency ?? '',
          status: row.status ?? 'Not Started'
        };

        if (this.editing) {
          const index = this.activities.findIndex(a => a.id === saved.id);
          if (index >= 0) this.activities[index] = saved;
        } else {
          this.activities = [...this.activities, saved].sort((a, b) => a.startDate.localeCompare(b.startDate));
        }

        this.showModal = false;
        this.editing = false;
        this.current = this.blankActivity();
        this.success = 'Schedule activity saved successfully.';
        this.cdr.detectChanges();
      },
      error: error => {
        this.error = this.message(error, 'Unable to save the schedule activity.');
      }
    });
  }

  remove(activity: Activity): void {
    if (!confirm(`Delete ${activity.name}?`)) return;
    this.deletingId = activity.id;
    this.error = '';
    this.success = '';
    this.api.deleteProjectScheduleActivity(activity.id).pipe(
      finalize(() => {
        this.deletingId = 0;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.activities = this.activities
          .filter(a => a.id !== activity.id)
          .map(a => a.dependency === activity.name ? { ...a, dependency: '' } : a);
        this.success = 'Schedule activity deleted.';
      },
      error: error => {
        this.error = this.message(error, 'Unable to delete the schedule activity.');
      }
    });
  }

  statusClass(status: string): string {
    return String(status).toLowerCase().replace(/\s+/g, '-');
  }
}
