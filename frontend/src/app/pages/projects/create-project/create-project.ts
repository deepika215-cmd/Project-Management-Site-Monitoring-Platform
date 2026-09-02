import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ProjectService } from '../../../services/project';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './create-project.html',
  styleUrl: './create-project.css'
})
export class CreateProject implements OnInit {
  project = {
    name: '', location: '', description: '', budget: null as number | null,
    startDate: '', completionDate: '', status: 'Planning', managerId: 0, manager: ''
  };

  loading = false;
  loadingManager = true;
  errorMessage = '';
  successMessage = '';

  constructor(
    private router: Router,
    private projectService: ProjectService,
    private api: Api
  ) {}

  ngOnInit(): void {
    this.loadManager();
  }

  private loadManager(): void {
    const cached = localStorage.getItem('currentUser');
    if (cached) {
      try {
        this.setManager(JSON.parse(cached));
      } catch {
        // A fresh /auth/me request below is the source of truth.
      }
    }

    if (!localStorage.getItem('token')) {
      this.loadingManager = false;
      this.errorMessage = 'You must be logged in before creating a project.';
      return;
    }

    this.api.getCurrentUser().subscribe({
      next: user => {
        this.setManager(user);
        this.loadingManager = false;
        if (!this.project.managerId) {
          this.errorMessage = 'The authenticated user could not be assigned as project manager.';
        }
      },
      error: err => {
        this.loadingManager = false;
        this.errorMessage = err?.error?.detail || 'Unable to load the authenticated user. Please log in again.';
      }
    });
  }

  private setManager(user: any): void {
    const id = Number(user?.id || 0);
    if (id > 0) {
      this.project.managerId = id;
      this.project.manager = user?.name || user?.email || `User #${id}`;
    }
  }

  createProject(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (this.loadingManager || this.loading) return;

    if (!this.project.managerId) {
      this.errorMessage = 'Project manager information is not available. Please log in again.';
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
      description: this.project.description.trim() || 'No description provided',
      location: this.project.location.trim(),
      start_date: this.project.startDate,
      end_date: this.project.completionDate,
      budget: Number(this.project.budget),
      status: this.project.status,
      manager_id: Number(this.project.managerId)
    }).subscribe({
      next: created => {
        this.loading = false;
        this.successMessage = `Project "${created.project_name}" was saved successfully (ID ${created.id}).`;
        // Navigate to the real list so the newly persisted record is fetched
        // again from FastAPI instead of relying on local component state.
        this.router.navigate(['/projects'], { queryParams: { created: created.id } });
      },
      error: err => {
        this.loading = false;
        const detail = err?.error?.detail;
        this.errorMessage = Array.isArray(detail)
          ? detail.map((item: any) => item?.msg || 'Invalid value').join(', ')
          : detail || `Project creation failed (HTTP ${err?.status || 'unknown'}).`;
      }
    });
  }
}
