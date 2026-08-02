import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ProjectService } from '../../../services/project';

interface Project {
  name: string;
  code: string;
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
}

@Component({
  selector: 'app-create-project',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './create-project.html',
  styleUrl: './create-project.css'
})
export class CreateProject {

  project: Project = {

    name: '',
    code: '',
    category: '',
    priority: '',
    description: '',

    clientName: '',
    clientEmail: '',
    clientPhone: '',
    companyName: '',

    location: '',

    budget: null,
    startDate: '',
    completionDate: '',
    duration: '',

    manager: '',
    status: 'Planning',
    phase: 'Initiation',
    visibility: 'Internal'

  };

  constructor(
  private router: Router,
  private projectService: ProjectService
) {}

  createProject(): void {

this.projectService.addProject({

  id: this.project.code,
  name: this.project.name,
  category: this.project.category,
  priority: this.project.priority,
  description: this.project.description,

  clientName: this.project.clientName,
  clientEmail: this.project.clientEmail,
  clientPhone: this.project.clientPhone,
  companyName: this.project.companyName,

  location: this.project.location,

  budget: this.project.budget,
  startDate: this.project.startDate,
  completionDate: this.project.completionDate,
  duration: this.project.duration,

  manager: this.project.manager,
  status: this.project.status,
  phase: this.project.phase,
  visibility: this.project.visibility,

  progress: 0

});

  alert('Project created successfully!');

  this.router.navigate(['/site-engineer-projects']);

}

}