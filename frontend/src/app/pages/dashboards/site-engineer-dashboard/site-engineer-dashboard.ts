import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({ selector: 'app-site-engineer-dashboard', standalone: true, imports: [CommonModule, RouterLink, AppSidebarComponent], templateUrl: './site-engineer-dashboard.html', styleUrl: './site-engineer-dashboard.css' })
export class SiteEngineerDashboard implements OnInit {
  projects: any[] = []; progress: any[] = []; resources: any[] = []; loading = true; error = '';
  constructor(private api: Api) {}
  ngOnInit(): void {
    forkJoin({ projects: this.api.getProjects(), progress: this.api.getProjectProgress(), resources: this.api.getResourceUtilizationAnalytics() }).subscribe({
      next: data => { this.projects = Array.isArray(data.projects) ? data.projects : []; this.progress = Array.isArray(data.progress) ? data.progress : []; this.resources = Array.isArray(data.resources) ? data.resources : []; this.loading = false; },
      error: err => { this.loading = false; this.error = err?.error?.detail || 'Unable to load site monitoring data.'; }
    });
  }
  progressFor(id: number): number { return Number(this.progress.find(p => Number(p.project_id) === Number(id))?.progress || 0); }
  resourceUtilization(): number { const rows = this.resources; const total = rows.reduce((s, r) => s + Number(r.total_quantity ?? r.quantity ?? 0), 0); const allocated = rows.reduce((s, r) => s + Number(r.allocated_quantity ?? 0), 0); return total ? Math.round(allocated / total * 100) : 0; }
}
