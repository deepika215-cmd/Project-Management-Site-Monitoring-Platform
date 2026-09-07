import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ProjectService } from '../../services/project';
import { Api } from '../../services/api';
import { finalize, timeout } from 'rxjs/operators';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-site-engineer-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './site-engineer-create-project.html',
  styleUrl: './site-engineer-create-project.css'
})
export class SiteEngineerCreateProject implements OnInit {
  project = {
    name: '', location: '', description: '', budget: null as number | null,
    startDate: '', completionDate: '', status: 'Planning', managerId: 0
  };

  managers: any[] = [];
  loading = false;
  loadingManagers = true;
  errorMessage = '';
  successMessage = '';

  constructor(
    private router: Router,
    private projectService: ProjectService,
    private api: Api,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.api.getCurrentUser().subscribe({
      next: user => {
        if (String(user?.role || '').toUpperCase() !== 'SITE_ENGINEER') {
          this.loadingManagers = false;
          this.errorMessage = 'This page is only available to Site Engineers.';
          return;
        }
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.loadManagers();
      },
      error: err => {
        this.loadingManagers = false;
        this.errorMessage = err?.error?.detail || 'Unable to verify the logged-in Site Engineer.';
      }
    });
  }

  private loadManagers(): void {
    this.api.getAvailableProjectManagers().subscribe({
      next: rows => {
        this.managers = Array.isArray(rows) ? rows : [];
        if (this.managers.length === 1) this.project.managerId = Number(this.managers[0].id);
        this.loadingManagers = false;
        if (!this.managers.length) this.errorMessage = 'No active Project Manager is available. Ask an Administrator to create or activate a Project Manager account.';
      },
      error: err => {
        this.loadingManagers = false;
        this.errorMessage = err?.error?.detail || 'Unable to load available Project Managers.';
      }
    });
  }

  createProject(): void {
    this.errorMessage = '';
    this.successMessage = '';
    if (this.loading || this.loadingManagers) return;

    if (!this.project.managerId) {
      this.errorMessage = 'Please select a Project Manager for this project.';
      return;
    }
    if (!this.project.name.trim() || !this.project.location.trim() || !this.project.startDate || !this.project.completionDate || this.project.budget === null) {
      this.errorMessage = 'Please complete all required fields before creating the project.';
      return;
    }
    if (Number(this.project.budget) < 0) {
      this.errorMessage = 'Budget cannot be negative.';
      return;
    }
    if (new Date(this.project.completionDate) < new Date(this.project.startDate)) {
      this.errorMessage = 'End date cannot be before the start date.';
      return;
    }

    this.loading = true;
    this.projectService.createProject({
      project_name: this.project.name.trim(),
      project_code: null as any,
      project_category: 'Residential',
      priority: 'Medium',
      description: this.project.description.trim() || 'No description provided',
      location: this.project.location.trim(),
      start_date: this.project.startDate,
      end_date: this.project.completionDate,
      budget: Number(this.project.budget),
      status: this.project.status,
      manager_id: Number(this.project.managerId)
    }).pipe(
      timeout(10000),
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: created => {
        this.loading = false;
        this.successMessage = `Project "${created.project_name}" was created successfully.`;
        this.router.navigate(['/projects'], { queryParams: { created: created.id } });
      },
      error: err => {
        this.loading = false;
        const detail = err?.error?.detail;
        if (err?.name === 'TimeoutError') {
          this.errorMessage = 'The server took too long to save the project. Please check the backend terminal and try again.';
          this.cdr.detectChanges();
          return;
        }
        this.errorMessage = Array.isArray(detail)
          ? detail.map((item: any) => item?.msg || 'Invalid value').join(', ')
          : detail || `Project creation failed (HTTP ${err?.status || 'unknown'}).`;
      }
    });
  }
}
