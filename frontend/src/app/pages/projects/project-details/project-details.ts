import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProjectService, Project } from '../../../services/project';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';
import { catchError, finalize, of, timeout } from 'rxjs';

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
  currentRole = '';
  currentUserId = 0;


  constructor(private route: ActivatedRoute, private router: Router, private projectService: ProjectService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.syncCurrentUser();
    this.route.paramMap.subscribe(() => this.loadProject());
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
      this.cdr.detectChanges();
      return;
    }

    // The project list endpoint is already known to be the persisted source
    // used by the My Projects page. Resolve the detail page from that list
    // first so a slow/unresponsive /projects/{id} request cannot leave the
    // user stuck on an endless loading screen.
    this.projectService.getProjects().pipe(timeout(10000), catchError(err => { this.errorMessage = this.getError(err, 'Unable to load the project list.'); return of([]); })).subscribe({
      next: projects => {
        const match = (Array.isArray(projects) ? projects : []).find(p => Number(p.id) === id);
        if (!match) {
          this.loading = false;
          this.errorMessage = `Project #${id} was not found in the persisted project list.`;
          this.cdr.detectChanges();
          return;
        }

        this.project = this.projectService.toViewModel(match);
        this.loading = false;
        this.cdr.detectChanges();
        this.loadTracking(id);
        this.loadMilestones(id);
      },
      error: err => {
        // Only use the single-project endpoint as a fallback.
        this.projectService.getProject(id).pipe(timeout(10000)).subscribe({
          next: backendProject => {
            this.project = this.projectService.toViewModel(backendProject);
            this.loading = false;
            this.cdr.detectChanges();
            this.loadTracking(id);
            this.loadMilestones(id);
          },
          error: fallbackErr => {
            this.loading = false;
            this.errorMessage = fallbackErr?.error?.detail || err?.error?.detail || 'Project could not be loaded. Confirm the backend is running.';
            this.cdr.detectChanges();
          }
        });
      }
    });
  }

  private loadTracking(id: number): void {
    this.projectService.getTracking(id).pipe(timeout(8000), catchError(() => of(null))).subscribe({
      next: tracking => { this.tracking = tracking; if (this.project) this.project.progress = Number(tracking?.progress ?? this.project.progress ?? 0); this.cdr.detectChanges(); },
      error: err => { this.tracking = null; if (err?.status && err.status !== 404) this.errorMessage = err?.error?.detail || 'Unable to load tracking.'; }
    });
  }

  private loadMilestones(id: number): void {
    this.projectService.getMilestones().pipe(timeout(8000), catchError(() => of([]))).subscribe({
      next: (items: any[]) => {
        this.milestones = (Array.isArray(items) ? items : []).filter(item => Number(item.project_id) === id).map(item => ({ name:item.title, plannedDate:item.due_date, status:item.status, description:item.description }));
        this.cdr.detectChanges();
      },
      error: () => this.milestones = []
    });
  }

  goBackToProjects(): void {
    // Every role uses the shared persisted project list route. Passing refresh
    // forces the Assigned Projects page to reload the latest backend records.
    this.router.navigate(['/projects'], { queryParams: { refresh: Date.now() } });
  }

  editProject(): void {
    if (!this.project || !this.canEditProject()) return;
    this.router.navigate(['/projects/update-project', this.project.id]);
  }

  deleteProject(): void {
    if (!this.project || this.deleting || !this.canDeleteProject()) return;
    if (!confirm(`Delete project "${this.project.name}"? This cannot be undone.`)) return;
    this.deleting = true;
    this.errorMessage = '';
    this.projectService.deleteProject(this.project.id).pipe(
      timeout(10000),
      finalize(() => { this.deleting = false; this.cdr.detectChanges(); })
    ).subscribe({
      next: () => this.goBackToProjects(),
      error: err => { this.errorMessage = this.getError(err, 'Unable to delete the project. Only Admin can delete projects.'); }
    });
  }

  canManageProjectControls(): boolean {
    return this.currentRole === 'ADMIN' || this.currentRole === 'PROJECT_MANAGER';
  }

  canEditProject(): boolean {
    if (!this.project) return false;
    if (this.currentRole === 'ADMIN') return true;
    return this.currentRole === 'PROJECT_MANAGER' && (!this.currentUserId || Number(this.project.managerId) === Number(this.currentUserId));
  }

  canDeleteProject(): boolean {
    return this.currentRole === 'ADMIN';
  }

  get backLabel(): string {
    return this.currentRole === 'ADMIN' ? 'Projects' : 'Assigned Projects';
  }

  private syncCurrentUser(): void {
    try {
      const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
      this.currentRole = String(user?.role || '').toUpperCase();
      this.currentUserId = Number(user?.id ?? user?.user_id ?? user?.userId ?? 0);
    } catch {
      this.currentRole = '';
      this.currentUserId = 0;
    }
  }

  getStatusClass(status: string): string { return ({ Planning:'planning', 'In Progress':'in-progress', 'On Hold': 'on-hold', Completed:'completed', Closed:'closed' } as Record<string,string>)[status] || ''; }
  private getError(err: any, fallback: string): string { const detail = err?.error?.detail; return Array.isArray(detail) ? detail.map((x: any) => x?.msg || 'Invalid value').join(', ') : (detail || fallback); }
}
