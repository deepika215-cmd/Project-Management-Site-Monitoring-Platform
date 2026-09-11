import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, finalize, map, Observable, of, switchMap, throwError, timeout } from 'rxjs';
import { ProjectService } from '../../../services/project';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-update-project',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './update-project.html',
  styleUrl: './update-project.css'
})
export class UpdateProject implements OnInit {
  project: any = this.emptyProject();
  updateReason = '';
  projectId = 0;
  loading = true;
  saving = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private projectService: ProjectService,
    private cdr: ChangeDetectorRef,
    private zone: NgZone
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = Number(params.get('id'));
      this.projectId = id;

      if (!id) {
        this.project = this.emptyProject();
        this.errorMessage = 'Invalid project ID in the route.';
        this.loading = false;
        this.forceRefresh();
        return;
      }

      this.loadProject(id);
    });
  }

  loadProject(id: number = this.projectId): void {
    this.loading = true;
    this.saving = false;
    this.errorMessage = '';
    this.successMessage = '';
    this.project = this.emptyProject();
    this.forceRefresh();

    this.loadProjectFromBackend(id).pipe(
      finalize(() => {
        this.loading = false;
        this.forceRefresh();
      })
    ).subscribe({
      next: backendProject => {
        this.project = this.projectService.toViewModel(backendProject);
        this.project.id = Number(this.project.id || id);

        // Keep the update form usable even if an older demo row does not
        // contain every optional frontend field.
        this.project.category = this.project.category || 'Residential';
        this.project.priority = this.project.priority || 'Medium';
        this.project.status = this.project.status || 'Planning';
        this.project.description = this.project.description || 'No description provided';

        this.forceRefresh();
      },
      error: err => {
        this.project = this.emptyProject();
        this.errorMessage = this.getError(
          err,
          `Unable to load Project #${id}. Check that FastAPI is running and that this user has permission to edit the project.`
        );
        this.forceRefresh();
      }
    });
  }

  updateProject(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.projectId || !this.project?.id) {
      this.errorMessage = 'Project was not loaded. Please click Refresh and try again.';
      return;
    }

    if (!this.project.name?.trim() || !this.project.location?.trim() || !this.project.startDate || !this.project.completionDate || this.project.budget === null || this.project.budget === undefined || !this.project.managerId) {
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
      this.errorMessage = 'Closed projects cannot be modified by the backend.';
      return;
    }

    this.saving = true;
    this.forceRefresh();

    const payload = {
      project_name: this.project.name.trim(),
      project_code: this.project.code?.trim() || null,
      project_category: this.normalizeCategory(this.project.category),
      description: this.project.description?.trim() || 'No description provided',
      location: this.project.location.trim(),
      start_date: this.project.startDate,
      end_date: this.project.completionDate,
      budget: Number(this.project.budget),
      priority: this.normalizePriority(this.project.priority),
      status: this.project.status || 'Planning',
      manager_id: Number(this.project.managerId)
    };

    this.projectService.updateProject(this.projectId, payload).pipe(
      timeout({ first: 10000 }),
      finalize(() => {
        this.saving = false;
        this.forceRefresh();
      })
    ).subscribe({
      next: saved => {
        this.project = this.projectService.toViewModel(saved);
        this.successMessage = 'Project updated successfully.';
        this.router.navigate(['/projects/project-details', this.projectId], {
          queryParams: { updated: this.projectId, refresh: Date.now() }
        });
      },
      error: err => {
        this.errorMessage = this.getError(err, 'Project update failed. Check manager ID, project code and backend permissions.');
      }
    });
  }

  goBack(): void {
    if (this.projectId) {
      this.router.navigate(['/projects/project-details', this.projectId]);
    } else {
      this.router.navigate(['/projects']);
    }
  }

  private loadProjectFromBackend(id: number): Observable<any> {
    // Prefer the single-project endpoint. If it fails because of an old route,
    // stale auth, or backend response mismatch, fall back to the same project
    // list that the My Projects / Assigned Projects table already uses.
    return this.projectService.getProject(id).pipe(
      timeout({ first: 8000 }),
      catchError(primaryError =>
        this.projectService.getProjects().pipe(
          timeout({ first: 8000 }),
          map(projects => {
            const match = (Array.isArray(projects) ? projects : []).find(project => Number((project as any).id) === Number(id));
            if (!match) {
              throw primaryError;
            }
            return match;
          }),
          catchError(() => throwError(() => primaryError))
        )
      )
    );
  }

  private emptyProject(): any {
    return {
      id: 0,
      name: '',
      code: '',
      category: 'Residential',
      priority: 'Medium',
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
      progress: 0
    };
  }

  private normalizeCategory(value: string): string {
    const allowed = ['Residential', 'Commercial', 'Industrial', 'Infrastructure', 'Government'];
    return allowed.includes(value) ? value : 'Residential';
  }

  private normalizePriority(value: string): string {
    const allowed = ['Low', 'Medium', 'High', 'Critical'];
    return allowed.includes(value) ? value : 'Medium';
  }

  private forceRefresh(): void {
    this.zone.run(() => {
      setTimeout(() => this.cdr.detectChanges(), 0);
    });
  }

  private getError(err: any, fallback: string): string {
    if (err?.name === 'TimeoutError') {
      return 'Backend did not respond in time. Confirm FastAPI is running at http://localhost:8000 and click Refresh.';
    }

    const detail = err?.error?.detail || err?.message;

    if (Array.isArray(detail)) {
      return detail.map((item: any) => item?.msg || item?.message || 'Invalid value').join(', ');
    }

    return detail || fallback;
  }
}
