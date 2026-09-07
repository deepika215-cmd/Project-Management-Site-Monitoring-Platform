import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, map, Observable, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-project-overview',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './project-overview.html',
  styleUrl: './project-overview.css'
})
export class ProjectOverview implements OnInit {
  loading = false;
  refreshing = false;
  error = '';
  projects: any[] = [];
  progress: any[] = [];
  selectedProjectId: number | null = null;

  constructor(
    private api: Api,
    private cdr: ChangeDetectorRef,
    private zone: NgZone
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.refreshing = true;
    this.error = '';
    this.forceRefresh();

    forkJoin({
      projects: this.safeArray(this.api.getProjects(), 'projects'),
      progress: this.safeArray(this.api.getProjectProgress(), 'project progress')
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.refreshing = false;
        this.forceRefresh();
      })
    ).subscribe({
      next: data => {
        this.projects = data.projects.map(project => this.normalizeProject(project));
        this.progress = data.progress.map(row => this.normalizeProgress(row));

        const selectedStillExists = this.projects.some(project => Number(project.id) === Number(this.selectedProjectId));
        if (!selectedStillExists) {
          this.selectedProjectId = this.projects.length ? Number(this.projects[0].id) : null;
        }

        if (!this.projects.length) {
          this.error = 'No accessible projects were found. Create a project first, then open Project Overview again.';
        }
      },
      error: () => {
        this.projects = [];
        this.progress = [];
        this.selectedProjectId = null;
        this.error = 'Unable to load project overview. Check that the backend is running and login token is valid.';
      }
    });
  }

  onProjectChange(): void {
    this.forceRefresh();
  }

  get selectedProject(): any {
    return this.projects.find(project => Number(project.id) === Number(this.selectedProjectId)) || null;
  }

  get selectedProgress(): any {
    const row = this.progress.find(item => Number(item.project_id ?? item.projectId) === Number(this.selectedProjectId));
    return row || {
      progress: this.selectedProject?.progress ?? this.selectedProject?.completion_percentage ?? 0,
      completed_milestones: this.selectedProject?.completed_milestones ?? 0,
      total_milestones: this.selectedProject?.total_milestones ?? 0
    };
  }

  pct(value: any): number {
    return Math.max(0, Math.min(100, Number(value) || 0));
  }

  displayDate(value: any): string {
    return value || '—';
  }

  private safeArray(source$: Observable<any>, label: string): Observable<any[]> {
    return source$.pipe(
      timeout({ first: 5000 }),
      map(value => this.toArray(value)),
      catchError(error => {
        console.warn(`Project Overview: ${label} request failed`, error);
        return of([]);
      })
    );
  }

  private toArray(value: any): any[] {
    if (Array.isArray(value)) return value;
    if (Array.isArray(value?.data)) return value.data;
    if (Array.isArray(value?.projects)) return value.projects;
    if (Array.isArray(value?.items)) return value.items;
    if (Array.isArray(value?.results)) return value.results;
    return [];
  }

  private normalizeProject(project: any): any {
    return {
      ...project,
      id: Number(project?.id ?? project?.project_id ?? project?.projectId),
      project_name: project?.project_name || project?.name || project?.title || 'Unnamed Project',
      status: project?.status || project?.project_status || 'Planning',
      location: project?.location || project?.site_location || '—',
      start_date: project?.start_date || project?.startDate || project?.planned_start_date || null,
      end_date: project?.end_date || project?.endDate || project?.completion_date || project?.planned_end_date || null,
      description: project?.description || project?.project_description || ''
    };
  }

  private normalizeProgress(row: any): any {
    return {
      ...row,
      project_id: Number(row?.project_id ?? row?.projectId ?? row?.id),
      project_name: row?.project_name || row?.name || 'Project',
      total_milestones: Number(row?.total_milestones ?? row?.totalMilestones ?? 0),
      completed_milestones: Number(row?.completed_milestones ?? row?.completedMilestones ?? 0),
      progress: Number(row?.progress ?? row?.completion_percentage ?? row?.progress_percentage ?? 0)
    };
  }

  private forceRefresh(): void {
    this.zone.run(() => {
      setTimeout(() => this.cdr.detectChanges(), 0);
    });
  }
}
