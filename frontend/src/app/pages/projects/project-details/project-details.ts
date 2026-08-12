import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProjectService, Project } from '../../../services/project';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-project-details',
  standalone: true,
  imports: [CommonModule, RouterLink, AppSidebarComponent],
  templateUrl: './project-details.html',
  styleUrl: './project-details.css'
})
export class ProjectDetails implements OnInit {
  project!: Project;
  milestones: any[] = [];
  loading = true;
  deleting = false;
  errorMessage = '';
  tracking: any = null;

  constructor(private route: ActivatedRoute, private router: Router, private projectService: ProjectService) { }

  ngOnInit(): void {
    this.loadProject();
  }

  loadProject(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loading = true;
    this.errorMessage = '';
    this.project = undefined as any;
    this.tracking = null;
    this.milestones = [];

    if (!id) {
      this.errorMessage = 'Invalid project ID.';
      this.loading = false;
      return;
    }

    // The project list endpoint is already known to be the persisted source
    // used by the My Projects page. Resolve the detail page from that list
    // first so a slow/unresponsive /projects/{id} request cannot leave the
    // user stuck on an endless loading screen.
    this.projectService.getProjects().subscribe({
      next: projects => {
        const match = (Array.isArray(projects) ? projects : []).find(p => Number(p.id) === id);
        if (!match) {
          this.loading = false;
          this.errorMessage = `Project #${id} was not found in the persisted project list.`;
          return;
        }

        this.project = this.projectService.toViewModel(match);
        this.loading = false;
        this.loadTracking(id);
        this.loadMilestones(id);
      },
      error: err => {
        // Only use the single-project endpoint as a fallback.
        this.projectService.getProject(id).subscribe({
          next: backendProject => {
            this.project = this.projectService.toViewModel(backendProject);
            this.loading = false;
            this.loadTracking(id);
            this.loadMilestones(id);
          },
          error: fallbackErr => {
            this.loading = false;
            this.errorMessage = fallbackErr?.error?.detail || err?.error?.detail || 'Project could not be loaded. Confirm the backend is running.';
          }
        });
      }
    });
  }

  private loadTracking(id: number): void {
    this.projectService.getTracking(id).subscribe({
      next: tracking => { this.tracking = tracking; this.project.progress = Number(tracking?.progress ?? 0); },
      error: err => { this.tracking = null; if (err?.status && err.status !== 404) this.errorMessage = err?.error?.detail || 'Unable to load tracking.'; }
    });
  }

  private loadMilestones(id: number): void {
    this.projectService.getMilestones().subscribe({
      next: (items: any[]) => {
        this.milestones = (Array.isArray(items) ? items : []).filter(item => Number(item.project_id) === id).map(item => ({ name: item.title, plannedDate: item.due_date, status: item.status, description: item.description }));
      },
      error: () => this.milestones = []
    });
  }

  deleteProject(): void {
    if (!this.project || this.deleting) return;
    if (!confirm(`Delete project "${this.project.name}"? This cannot be undone.`)) return;
    this.deleting = true;
    this.errorMessage = '';
    this.projectService.deleteProject(this.project.id).subscribe({
      next: () => this.router.navigate(['/projects']),
      error: err => { this.deleting = false; this.errorMessage = err?.error?.detail || 'Unable to delete the project.'; }
    });
  }

  getStatusClass(status: string): string { return ({ Planning: 'planning', 'In Progress': 'in-progress', 'On Hold': 'on-hold', Completed: 'completed', Closed: 'closed' } as Record<string, string>)[status] || ''; }
}
