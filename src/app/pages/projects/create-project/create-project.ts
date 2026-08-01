import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

interface Project {
  name: string;
  code: string;
  category: string;
  priority: string;
  description: string;
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  location: string;
  budget: number | null;
  startDate: string;
  completionDate: string;
  manager: string;
  status: string;
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
    location: '',
    budget: null,
    startDate: '',
    completionDate: '',
    manager: '',
    status: 'Planning'

  };


  constructor(
    private router: Router
  ) {}


  createProject(): void {

    console.log(
      'Project Created:',
      this.project
    );


    alert(
      'Project created successfully!'
    );


    this.router.navigate(
      ['/projects']
    );

  }

}