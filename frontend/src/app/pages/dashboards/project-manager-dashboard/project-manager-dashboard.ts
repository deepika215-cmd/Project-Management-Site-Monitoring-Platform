import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-project-manager-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    AppSidebarComponent
  ],
  templateUrl: './project-manager-dashboard.html',
  styleUrls: ['./project-manager-dashboard.css']
})
export class ProjectManagerDashboard {

  totalProjects = 5;

  completedProjects = 1;

  activeProjects = 3;

  delayedProjects = 1;

  milestoneCompletion = 72;

  resourceUtilization = 68;

  totalWorkers = 120;

  totalEngineers = 18;

  totalContractors = 12;

  upcomingDeadlines = [
    {
      project: 'Green Valley Apartments',
      activity: 'Foundation Work',
      due: '2 Days'
    },
    {
      project: 'City Mall Construction',
      activity: 'Electrical Inspection',
      due: '5 Days'
    },
    {
      project: 'Industrial Warehouse',
      activity: 'Roof Casting',
      due: 'Tomorrow'
    }
  ];

  recentActivities = [
    'Structural Work completed successfully.',
    '20 workers assigned to Green Valley Apartments.',
    'Material request submitted for approval.',
    'Milestone approved by Project Manager.',
    'Equipment allocation updated.'
  ];

}