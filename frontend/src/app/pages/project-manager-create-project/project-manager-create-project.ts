import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ProjectService } from '../../services/project';
import { Api } from '../../services/api';
import { finalize, timeout } from 'rxjs/operators';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-project-manager-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './project-manager-create-project.html',
  styleUrl: './project-manager-create-project.css'
})
export class ProjectManagerCreateProject implements OnInit {
  project = {
    name: '', location: '', description: '', budget: null as number | null,
    startDate: '', completionDate: '', status: 'Planning', managerId: 0, manager: ''
  };

  loading = false;
  loadingManager = true;
  private authenticatedManagerId = 0;
  errorMessage = '';
  successMessage = '';

  constructor(
    private router: Router,
    private projectService: ProjectService,
    private api: Api,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadManager();
  }

  private loadManager(): void {
    const cached = localStorage.getItem('currentUser');
    if (cached) {
      try { this.setManager(JSON.parse(cached)); } catch { /* refresh below */ }
    }

    if (!localStorage.getItem('token')) {
      this.loadingManager = false;
      this.errorMessage = 'You must be logged in before creating a project.';
      return;
    }

    this.api.getCurrentUser().subscribe({
      next: user => {
        const role = String(user?.role || '').toUpperCase();
        if (role !== 'PROJECT_MANAGER') {
          this.loadingManager = false;
          this.errorMessage = 'This project creation page is only for Project Managers.';
          return;
        }
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.setManager(user);
        this.loadingManager = false;
      },
      error: err => {
        this.loadingManager = false;
        this.errorMessage = err?.error?.detail || 'Unable to load the authenticated Project Manager.';
      }
    });
  }

  private setManager(user: any): void {
    if (String(user?.role || '').toUpperCase() !== 'PROJECT_MANAGER') return;
    const id = Number(user?.id || 0);
    if (id > 0) {
      this.authenticatedManagerId = id;
      this.project.managerId = id;
      this.project.manager = user?.name || user?.email || `User #${id}`;
    }
  }

  createProject(): void {
    this.errorMessage = '';
    this.successMessage = '';
    if (this.loadingManager || this.loading) return;

    // Never trust a stale/form-edited manager id on the Project Manager page.
    // This page always assigns the new project to the authenticated PM.
    this.project.managerId = this.authenticatedManagerId;

    if (!this.project.managerId) {
      this.errorMessage = 'Project Manager information is not available. Please sign in again.';
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
