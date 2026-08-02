import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ProjectService, Project } from '../../services/project';

@Component({
  selector: 'app-site-engineer-projects',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './site-engineer-projects.html',
  styleUrl: './site-engineer-projects.css'
})
export class SiteEngineerProjects {

  projects: Project[] = [];

  constructor(private projectService: ProjectService) {
    this.projects = this.projectService.getProjects();
  }

}