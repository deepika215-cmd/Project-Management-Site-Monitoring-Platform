import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProjectService, Project } from '../../../services/project';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './project-list.html',
  styleUrl: './project-list.css'
})
export class ProjectList implements OnInit {
  searchText = '';
  selectedCategory = '';
  selectedStatus = '';
  projects: Project[] = [];
  filteredProjects: Project[] = [];
  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(private projectService: ProjectService, private route: ActivatedRoute, private router: Router, private cdr: ChangeDetectorRef) { }

  ngOnInit(): void {
    // Reload whenever navigation returns to this page with a creation/update
    // query parameter. This also handles Angular reusing the same component
    // instance instead of running ngOnInit a second time.
    this.route.queryParamMap.subscribe(params => {
      const created = params.get('created');
      const updated = params.get('updated');
      const deleted = params.get('deleted');
      if (created) {
        this.successMessage = `Project #${created} was created successfully.`;
      } else if (updated) {
        this.successMessage = `Project #${updated} was updated successfully.`;
      } else if (deleted) {
        this.successMessage = `Project #${deleted} was deleted successfully.`;
      } else {
        this.successMessage = '';
      }
      this.loadProjects();
      if (created || updated || deleted) {
        setTimeout(() => { this.successMessage = ''; this.cdr.markForCheck(); }, 5000);
      }
    });
  }

  refreshProjects(): void {
    this.searchText = '';
    this.selectedCategory = '';
    this.selectedStatus = '';
    this.loadProjects();
  }

  viewProject(id: number): void {
    this.router.navigate(['/projects/project-details', id]);
  }

  editProject(id: number): void {
    this.router.navigate(['/projects/update-project', id]);
  }

  loadProjects(): void {
    this.loading = true;
    this.errorMessage = '';
    this.projectService.getProjects().subscribe({
      next: data => {
        const rows = Array.isArray(data) ? data : [];
        this.projects = rows.map(p => this.projectService.toViewModel(p));
        this.filteredProjects = [...this.projects];
        this.loading = false;
        this.filterProjects();
        this.cdr.detectChanges();
        this.loadProgressForProjects();
      },
      error: err => {
        this.projects = [];
        this.filteredProjects = [];
        this.loading = false;
        this.errorMessage = this.getError(err, 'Unable to load projects from the backend.');
        this.cdr.detectChanges();
      }
    });
  }

  private loadProgressForProjects(): void {
    this.projects.forEach(project => {
      this.projectService.getTracking(project.id).subscribe({
        next: tracking => {
          project.progress = Math.max(0, Math.min(100, Number(tracking?.progress ?? 0)));
          this.filterProjects();
          this.cdr.detectChanges();
        },
        error: () => { project.progress = 0; }
      });
    });
  }

  filterProjects(): void {
    const search = this.searchText.trim().toLowerCase();
    this.filteredProjects = this.projects.filter(project =>
      (!search || project.name.toLowerCase().includes(search) || project.code.toLowerCase().includes(search) || project.location.toLowerCase().includes(search)) &&
      (!this.selectedCategory || project.category === this.selectedCategory) &&
      (!this.selectedStatus || project.status === this.selectedStatus)
    );
  }

  getProjectCount(status: string): number { return this.projects.filter(p => p.status === status).length; }

  deleteProject(project: Project): void {
    if (!confirm(`Delete project "${project.name}"? This cannot be undone.`)) return;
    this.loading = true;
    this.errorMessage = '';
    this.projectService.deleteProject(project.id).subscribe({
      next: () => {
        this.successMessage = `Project "${project.name}" was deleted.`;
        this.loadProjects();
        this.cdr.detectChanges();
      },
      error: err => {
        this.loading = false;
        this.errorMessage = this.getError(err, 'Unable to delete the project.');
      }
    });
  }

  clearFilters(): void {
    this.searchText = '';
    this.selectedCategory = '';
    this.selectedStatus = '';
    this.filterProjects();
  }

  getStatusClass(status: string): string {
    return ({ Planning: 'planning', 'In Progress': 'in-progress', 'On Hold': 'on-hold', Completed: 'completed', Closed: 'closed' } as Record<string, string>)[status] || '';
  }

  private getError(err: any, fallback: string): string {
    const detail = err?.error?.detail;
    if (Array.isArray(detail)) return detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
    return detail || fallback;
  }
}
