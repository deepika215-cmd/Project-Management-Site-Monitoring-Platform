import { Injectable } from '@angular/core';

export interface Project {

  id: string;
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