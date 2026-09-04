import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProjectService } from '../../../services/project';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-update-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './update-project.html',
  styleUrl: './update-project.css',
})
export class UpdateProject implements OnInit {
  project: any = {
    id: 0,
    name: '',
    code: '',
    category: '',
    priority: '',
    description: '',
    clientName: '',
    clientEmail: '',
    clientPhone: '',
    location: '',
    budget: 0,
    startDate: '',
    completionDate: '',
    manager: '',
    managerId: 0,
    status: 'Planning',
    progress: 0,
  };

  projectId = 0;
  loading = true;
  saving = false;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private projectService: ProjectService,
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    console.log('URL Project ID:', id);

    this.projectId = Number(id);

    if (!this.projectId || this.projectId <= 0) {
      this.loading = false;
      this.errorMessage = 'Invalid project ID.';
      return;
    }

    this.loadProject();
  }

  private loadProject(): void {
    this.loading = true;
    this.errorMessage = '';

    console.log('Loading project ID:', this.projectId);

    this.projectService.getProject(this.projectId).subscribe({
      next: (data) => {
        console.log('Project received:', data);

        if (!data) {
          this.errorMessage = 'Project data was not found.';
          this.loading = false;
          return;
        }

        this.project = this.projectService.toViewModel(data);

        console.log('Project loaded:', this.project);
        console.log('Project loaded ID:', this.project.id);

        this.loading = false;
      },

      error: (err) => {
        console.error('Project loading error:', err);

        this.loading = false;

        const detail = err?.error?.detail;

        if (Array.isArray(detail)) {
          this.errorMessage = detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
        } else {
          this.errorMessage = detail || 'Unable to load project from the backend.';
        }
      },
    });
  }
  cancel(): void {
    this.router.navigate(['/projects']);
  }

  updateProject(): void {
    this.errorMessage = '';

    if (this.loading || this.saving) {
      return;
    }

    if (
      !this.project.name?.trim() ||
      !this.project.location?.trim() ||
      !this.project.startDate ||
      !this.project.completionDate ||
      this.project.budget === null ||
      this.project.budget === undefined ||
      !this.project.managerId
    ) {
      this.errorMessage = 'Required project fields are missing.';
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

    if (this.project.status === 'Closed') {
      this.errorMessage = 'Closed projects cannot be modified. Change the status first.';
      return;
    }

    this.saving = true;

    const updateData = {
      project_name: this.project.name.trim(),
      description: this.project.description?.trim() || 'No description provided',
      location: this.project.location.trim(),
      start_date: this.project.startDate,
      end_date: this.project.completionDate,
      budget: Number(this.project.budget),
      status: this.project.status,
      manager_id: Number(this.project.managerId),
    };

    console.log('Updating project:', this.projectId);
    console.log('Update data:', updateData);

    this.projectService.updateProject(this.projectId, updateData).subscribe({
      next: (response) => {
        console.log('Project updated successfully:', response);

        this.saving = false;

        this.router.navigate(['/projects/project-details', this.projectId], {
          queryParams: {
            updated: this.projectId,
          },
        });
      },

      error: (err) => {
        console.error('Project update error:', err);

        this.saving = false;

        const detail = err?.error?.detail;

        if (Array.isArray(detail)) {
          this.errorMessage = detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
        } else {
          this.errorMessage = detail || 'Project update failed.';
        }
      },
    });
  }
}
