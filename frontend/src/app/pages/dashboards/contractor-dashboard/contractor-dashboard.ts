import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({ selector: 'app-contractor-dashboard', standalone: true, imports: [CommonModule, RouterLink], templateUrl: './contractor-dashboard.html', styleUrl: './contractor-dashboard.css' })
export class ContractorDashboard implements OnInit {
  projects: any[] = []; procurements: any[] = []; loading = true; error = '';

  constructor(private api: Api) { }

  ngOnInit(): void {
    forkJoin({ projects: this.api.getProjects(), procurements: this.api.getProcurements() }).subscribe({
      next: ({ projects, procurements }) => { this.projects = Array.isArray(projects) ? projects : []; this.procurements = Array.isArray(procurements) ? procurements : []; this.loading = false; },
      error: err => { this.loading = false; this.error = err?.error?.detail || 'Unable to load contractor overview.'; }
    });
  }

  get activeCount(): number { return this.projects.filter(p => p.status === 'In Progress').length; }
  get completedCount(): number { return this.projects.filter(p => p.status === 'Completed' || p.status === 'Closed').length; }
  get pendingProcurementCount(): number { return this.procurements.filter(p => String(p.status || '').toLowerCase().includes('pending')).length; }
  statusClass(status: string): string { return String(status || '').toLowerCase().replace(/\s+/g, '-'); }
}
