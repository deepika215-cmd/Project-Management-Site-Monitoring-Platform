import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

interface ProjectRow {
  id: number;
  project_name: string;
  status: string;
  start_date: string;
  end_date: string;
  progress: number;
}

@Component({
  selector: 'app-project-manager-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, AppSidebarComponent],
  templateUrl: './project-manager-dashboard.html',
  styleUrls: ['./project-manager-dashboard.css']
})
export class ProjectManagerDashboard implements OnInit {
  loading = true;
  error = '';
  projects: ProjectRow[] = [];
  upcomingDeadlines: ProjectRow[] = [];
  totalProjects = 0;
  completedProjects = 0;
  activeProjects = 0;
  delayedProjects = 0;
  milestoneCompletion = 0;
  resourceUtilization = 0;
  totalWorkers = 0;
  totalEngineers = 0;
  totalContractors = 0;

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.error = '';

    forkJoin({
      projects: this.api.getProjects(),
      progress: this.api.getProjectProgress(),
      resources: this.api.getResourceUtilizationAnalytics(),
      workers: this.api.getWorkers()
    }).subscribe({
      next: ({ projects, progress, resources, workers }) => {
        const projectRows = Array.isArray(projects) ? projects : [];
        const progressRows = Array.isArray(progress) ? progress : [];
        const resourceRows = Array.isArray(resources) ? resources : [];
        const workerRows = Array.isArray(workers) ? workers : [];
        const progressMap = new Map<number, number>(
          progressRows.map((row: any) => [Number(row.project_id), Number(row.progress) || 0])
        );

        this.projects = projectRows.map((project: any) => ({
          id: Number(project.id),
          project_name: project.project_name || 'Unnamed project',
          status: project.status || 'Planning',
          start_date: project.start_date,
          end_date: project.end_date,
          progress: Math.max(0, Math.min(100, progressMap.get(Number(project.id)) ?? 0))
        }));

        this.totalProjects = this.projects.length;
        this.completedProjects = this.projects.filter(p => p.status === 'Completed' || p.status === 'Closed').length;
        this.activeProjects = this.projects.filter(p => p.status === 'In Progress').length;
        this.delayedProjects = this.projects.filter(p => this.isOverdue(p)).length;
        this.milestoneCompletion = this.projects.length
          ? Math.round(this.projects.reduce((sum, project) => sum + project.progress, 0) / this.projects.length)
          : 0;

        const totalResourceUnits = resourceRows.reduce((sum: number, row: any) =>
          sum + (Number(row.total_quantity ?? row.quantity ?? 0) || (Number(row.available ?? 0) + Number(row.allocated ?? row.allocated_quantity ?? 0))), 0);
        const allocatedUnits = resourceRows.reduce((sum: number, row: any) =>
          sum + (Number(row.allocated_quantity ?? row.allocated ?? 0) || 0), 0);
        this.resourceUtilization = totalResourceUnits > 0
          ? Math.round((allocatedUnits / totalResourceUnits) * 100)
          : 0;

        this.totalWorkers = workerRows.length;
        this.totalEngineers = workerRows.filter((row: any) => /engineer/i.test(row.role || '')).length;
        this.totalContractors = workerRows.filter((row: any) => /contractor/i.test(row.role || '')).length;

        this.upcomingDeadlines = [...this.projects]
          .filter(project => project.status !== 'Completed' && project.status !== 'Closed' && !!project.end_date)
          .sort((a, b) => new Date(a.end_date).getTime() - new Date(b.end_date).getTime())
          .slice(0, 5);

        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.error = this.errorMessage(err, 'Unable to load the Project Manager dashboard from the backend.');
      }
    });
  }

  isOverdue(project: ProjectRow): boolean {
    if (!project.end_date || project.status === 'Completed' || project.status === 'Closed') return false;
    return new Date(project.end_date).getTime() < new Date().setHours(0, 0, 0, 0);
  }

  deadlineLabel(project: ProjectRow): string {
    if (!project.end_date) return 'Not set';
    const days = Math.ceil((new Date(project.end_date).getTime() - Date.now()) / 86400000);
    if (days < 0) return `${Math.abs(days)} day(s) overdue`;
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    return `${days} days`;
  }

  statusClass(status: string): string {
    return status.toLowerCase().replace(/\s+/g, '-');
  }

  private errorMessage(err: any, fallback: string): string {
    const detail = err?.error?.detail;
    if (Array.isArray(detail)) return detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
    return detail || err?.error?.message || fallback;
  }
}
