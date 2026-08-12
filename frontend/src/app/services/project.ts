import { Injectable } from '@angular/core';
<<<<<<< HEAD
import { Observable } from 'rxjs';
import { Api } from './api';

export interface Project {
  id: number;
  code: string;
=======

export interface Project {

  id: string;
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
  name: string;
  category: string;
  priority: string;
  description: string;
<<<<<<< HEAD
=======

>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  companyName: string;
<<<<<<< HEAD
  location: string;
=======

  location: string;

>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
  budget: number | null;
  startDate: string;
  completionDate: string;
  duration: string;
<<<<<<< HEAD
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
=======

  manager: string;
  status: string;
  phase: string;
  visibility: string;

  progress: number;

}

@Injectable({
  providedIn: 'root'
})
export class ProjectService {

  private projects: Project[] = [
  {
    id: 'BT-001',
    name: 'Green Valley Apartments',
    category: 'Residential',
    priority: 'High',
    description: 'Residential apartment construction project.',
    clientName: 'Green Valley Developers',
    clientEmail: 'client@greenvalley.com',
    clientPhone: '+91 9876543210',
    companyName: 'Green Valley Developers',
    location: 'Chennai',
    budget: 5000000,
    startDate: '2026-01-15',
    completionDate: '2027-06-30',
    duration: '18 Months',
    manager: 'Raj Kumar',
    status: 'Completed',
    phase: 'Execution',
    visibility: 'Internal',
    progress: 100
  },
  {
    id: 'BT-002',
    name: 'City Mall Construction',
    category: 'Commercial',
    priority: 'Medium',
    description: 'Commercial shopping mall construction.',
    clientName: 'City Developers',
    clientEmail: 'client@citydevelopers.com',
    clientPhone: '+91 9876543211',
    companyName: 'City Developers',
    location: 'Coimbatore',
    budget: 10000000,
    startDate: '2026-03-01',
    completionDate: '2027-09-30',
    duration: '18 Months',
    manager: 'Priya Sharma',
    status: 'In Progress',
    phase: 'Planning',
    visibility: 'Internal',
    progress: 65
  },
  {
    id: 'BT-003',
    name: 'Industrial Warehouse',
    category: 'Industrial',
    priority: 'Low',
    description: 'Warehouse and logistics center construction.',
    clientName: 'Industrial Solutions',
    clientEmail: 'client@industrialsolutions.com',
    clientPhone: '+91 9876543212',
    companyName: 'Industrial Solutions',
    location: 'Bangalore',
    budget: 7500000,
    startDate: '2026-06-01',
    completionDate: '2027-12-31',
    duration: '18 Months',
    manager: 'Vikram Singh',
    status: 'Pending',
    phase: 'Planning',
    visibility: 'Internal',
    progress: 20
  }
];
  getProjects(): Project[] {
    return this.projects;
  }

  addProject(project: Project) {
    this.projects.push(project);
  }
  getProjectById(id: string): Project | undefined {
  return this.projects.find(project => project.id === id);
  }

}
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
