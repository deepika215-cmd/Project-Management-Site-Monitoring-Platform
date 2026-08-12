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
    return {
      id: project.id,
      code: `BT-${String(project.id).padStart(3, '0')}`,
      name: project.project_name,
      category: 'Construction',
      priority: 'Standard',
      description: project.description,
      clientName: 'Not provided by backend',
      clientEmail: '',
      clientPhone: '',
      companyName: '',
      location: project.location,
      budget: project.budget,
      startDate: project.start_date,
      completionDate: project.end_date,
      duration: this.calculateDuration(project.start_date, project.end_date),
      manager: `User #${project.manager_id}`,
      managerId: project.manager_id,
      status: project.status,
      phase: project.status === 'Planning' ? 'Planning' : 'Execution',
      visibility: 'Internal',
      progress: 0
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
