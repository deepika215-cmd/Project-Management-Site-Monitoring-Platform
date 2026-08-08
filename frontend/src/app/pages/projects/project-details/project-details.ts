import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ProjectService, Project } from '../../../services/project';

@Component({
  selector: 'app-project-details',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './project-details.html',
  styleUrl: './project-details.css'
})
export class ProjectDetails {

  project!: Project;


  milestones = [

    {
      name: 'Foundation Completed',
      plannedDate: '2026-03-15',
      status: 'Completed'
    },

    {
      name: 'Structural Work Completed',
      plannedDate: '2026-07-30',
      status: 'In Progress'
    },

    {
      name: 'Electrical Work Completed',
      plannedDate: '2026-10-30',
      status: 'Pending'
    },

    {
      name: 'Final Inspection',
      plannedDate: '2027-05-30',
      status: 'Pending'
    }

  ];


  siteEngineers = [

    {
      name: 'Arun Kumar',
      zone: 'Block A'
    },

    {
      name: 'Vijay Kumar',
      zone: 'Block B'
    },

    {
      name: 'Suresh Kumar',
      zone: 'Block C'
    }

  ];


  contractors = [

    {
      name: 'ABC Civil Contractors',
      specialization: 'Civil Construction'
    },

    {
      name: 'PowerTech Electricals',
      specialization: 'Electrical Work'
    },

    {
      name: 'Aqua Plumbing Services',
      specialization: 'Plumbing'
    },

    {
      name: 'Perfect Finish Interiors',
      specialization: 'Interior Finishing'
    }

  ];


  constructor(
  private route: ActivatedRoute,
  private projectService: ProjectService
) {

  const projectId = this.route.snapshot.paramMap.get('id');

  if (projectId) {

    const foundProject = this.projectService.getProjectById(projectId);

    if (foundProject) {
      this.project = foundProject;
    }

  }

}


  getStatusClass(
    status: string
  ): string {

    switch (status) {

      case 'Planning':
        return 'planning';

      case 'In Progress':
        return 'in-progress';

      case 'On Hold':
        return 'on-hold';

      case 'Completed':
        return 'completed';

      case 'Closed':
        return 'closed';

      default:
        return '';

    }

  }

}