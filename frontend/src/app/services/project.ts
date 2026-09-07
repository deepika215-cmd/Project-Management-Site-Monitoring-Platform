import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Api } from './api';

export interface Project {
  id: number;
  code: string;
  name: string;
  category: string;
  priority: string;
  description: string;
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  companyName: string;
  location: string;
  budget: number | null;
  startDate: string;
  completionDate: string;
  duration: string;
  manager: string;
  managerId: number;
  status: string;
  phase: string;
  visibility: string;
  progress: number;
}

export interface BackendProject {
  id: number;
  project_name: string;
  project_code?: string | null;
  code?: string | null;
  name?: string | null;
  project_category?: string;
  category?: string;
  priority?: string;
  manager_name?: string | null;
  managerName?: string | null;
  description: string;
  location: string;
  start_date: string;
  end_date: string;
  budget: number;
  status: string;
  manager_id: number;
}

@Injectable({ providedIn: 'root' })
export class ProjectService {
  constructor(private api: Api) {}

  getProjects(): Observable<BackendProject[]> {
    return this.api.getProjects() as Observable<BackendProject[]>;
  }

  getProject(id: number): Observable<BackendProject> {
    return this.api.getProject(id) as Observable<BackendProject>;
  }

  createProject(project: Omit<BackendProject, 'id'>): Observable<BackendProject> {
    return this.api.createProject(project) as Observable<BackendProject>;
  }

  updateProject(id: number, project: Omit<BackendProject, 'id'>): Observable<BackendProject> {
    return this.api.updateProject(id, project) as Observable<BackendProject>;
  }

  deleteProject(id: number): Observable<unknown> {
    return this.api.deleteProject(id);
  }

  updateStatus(id: number, status: string): Observable<BackendProject> {
    return this.api.updateProjectStatus(id, { status }) as Observable<BackendProject>;
  }

  closeProject(id: number): Observable<BackendProject> {
    return this.api.closeProject(id) as Observable<BackendProject>;
  }

  getTracking(id: number): Observable<any> {
    return this.api.getProjectTracking(id);
  }

  getMilestones(): Observable<any[]> {
    return this.api.getMilestones() as Observable<any[]>;
  }

  toViewModel(project: BackendProject): Project {
    const p: any = project || {};
    const start = p.start_date || p.startDate || '';
    const end = p.end_date || p.endDate || p.completionDate || '';
    const managerId = Number(p.manager_id ?? p.managerId ?? 0);
    const managerName = p.manager_name || p.managerName || (managerId ? `Project Manager #${managerId}` : 'Project Manager');
    return {
      id: Number(p.id),
      code: p.project_code || p.code || `BT-${String(p.id).padStart(3, '0')}`,
      name: p.project_name || p.name || 'Unnamed project',
      category: p.project_category || p.category || 'Construction',
      priority: p.priority || p.project_priority || 'Standard',
      description: p.description || '',
      clientName: p.client_name || 'Demo Client',
      clientEmail: p.client_email || '',
      clientPhone: p.client_phone || '',
      companyName: p.company_name || '',
      location: p.location || '',
      budget: Number(p.budget ?? 0),
      startDate: start,
      completionDate: end,
      duration: this.calculateDuration(start, end),
      manager: managerName,
      managerId,
      status: p.status || 'Planning',
      phase: (p.status || '') === 'Planning' ? 'Planning' : 'Execution',
      visibility: 'Internal',
      progress: Number(p.progress ?? 0)
    };
  }

  private calculateDuration(start: string, end: string): string {
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) return '';
    const months = Math.max(0, (endDate.getFullYear() - startDate.getFullYear()) * 12 + endDate.getMonth() - startDate.getMonth());
    return `${months} month${months === 1 ? '' : 's'}`;
  }
}
