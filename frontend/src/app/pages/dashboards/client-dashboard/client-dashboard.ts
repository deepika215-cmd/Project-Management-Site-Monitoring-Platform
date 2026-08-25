import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-client-dashboard', standalone: true, imports: [CommonModule, RouterLink],
  templateUrl: './client-dashboard.html', styleUrl: './client-dashboard.css'
})
export class ClientDashboard implements OnInit {
  projects: any[] = []; loading = true; error = '';
  totalBudget = 0; activeProjects = 0; completedProjects = 0; averageProgress = 0;

  constructor(private api: Api) {}

  ngOnInit(): void {
    forkJoin({ projects: this.api.getProjects(), progress: this.api.getProjectProgress() }).subscribe({
      next: ({ projects, progress }) => {
        const rows = Array.isArray(projects) ? projects : [];
        const progressMap = new Map<number, number>((Array.isArray(progress) ? progress : []).map((p: any) => [Number(p.project_id), Number(p.progress) || 0]));
        this.projects = rows.map((p: any) => ({ ...p, progress: progressMap.get(Number(p.id)) ?? 0 }));
        this.totalBudget = this.projects.reduce((sum, p) => sum + (Number(p.budget) || 0), 0);
        this.activeProjects = this.projects.filter(p => p.status === 'In Progress').length;
        this.completedProjects = this.projects.filter(p => p.status === 'Completed' || p.status === 'Closed').length;
        this.averageProgress = this.projects.length ? Math.round(this.projects.reduce((sum, p) => sum + p.progress, 0) / this.projects.length) : 0;
        this.loading = false;
      },
      error: err => { this.loading = false; this.error = err?.error?.detail || 'Unable to load project data.'; }
    });
  }

  statusClass(status: string): string { return String(status || '').toLowerCase().replace(/\s+/g, '-'); }
}
