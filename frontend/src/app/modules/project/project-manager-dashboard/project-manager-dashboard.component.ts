import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface SidebarItem {
  label: string;
  icon: string;
  active?: boolean;
}

interface ProjectCard {
  name: string;
  manager: string;
  progress: number;
  deadline: string;
  status: string;
}

interface ResourceItem {
  label: string;
  value: string;
  detail: string;
}

interface WorkforceSummary {
  label: string;
  value: string;
  detail: string;
}

interface ActivityItem {
  title: string;
  project: string;
  status: string;
  due: string;
}

interface UpdateItem {
  title: string;
  time: string;
  detail: string;
}

@Component({
  selector: 'app-project-manager-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './project-manager-dashboard.component.html',
  styleUrl: './project-manager-dashboard.component.scss'
})
export class ProjectManagerDashboardComponent {
  navItems: SidebarItem[] = [
    { label: 'Dashboard', icon: '📊', active: true },
    { label: 'My Projects', icon: '📁' },
    { label: 'Project Milestones', icon: '🏁' },
    { label: 'Site Progress', icon: '🚧' },
    { label: 'Resource Allocation', icon: '🧱' },
    { label: 'Workforce', icon: '👷' },
    { label: 'Procurement Requests', icon: '🛒' },
    { label: 'Budget Tracking', icon: '💰' },
    { label: 'Reports', icon: '📈' },
    { label: 'Notifications', icon: '🔔' },
    { label: 'Profile', icon: '👤' }
  ];

  projects: ProjectCard[] = [
    { name: 'River Bridge Expansion', manager: 'Amit Sharma', progress: 74, deadline: '2026-11-15', status: 'On track' },
    { name: 'Metro Station Upgrade', manager: 'Neha Gupta', progress: 58, deadline: '2026-12-02', status: 'At risk' },
    { name: 'Road Safety Audit', manager: 'Rahul Patel', progress: 91, deadline: '2026-10-04', status: 'Completed' }
  ];

  milestones = [
    { label: 'Design Approval', value: 100 },
    { label: 'Material Procurement', value: 85 },
    { label: 'Site Mobilization', value: 65 },
    { label: 'Concrete Pouring', value: 40 }
  ];

  resourceUtilization: ResourceItem[] = [
    { label: 'Equipment Usage', value: '82%', detail: 'Cranes and concrete mixers' },
    { label: 'Material Utilization', value: '68%', detail: 'Cement, steel, aggregates' },
    { label: 'Budget Utilization', value: '74%', detail: 'Remaining budget: ₹8.4M' }
  ];

  workforceSummary: WorkforceSummary[] = [
    { label: 'Active Teams', value: '14', detail: 'On-site and field support' },
    { label: 'Available Staff', value: '37', detail: 'Engineers, supervisors, labour' },
    { label: 'Overtime Hours', value: '62', detail: 'Last 7 days' }
  ];

  delayedActivities: ActivityItem[] = [
    { title: 'Soil stabilization', project: 'River Bridge Expansion', status: 'Delayed', due: '2026-08-24' },
    { title: 'Permit clearance', project: 'Metro Station Upgrade', status: 'Delayed', due: '2026-09-05' },
    { title: 'Material delivery', project: 'Road Safety Audit', status: 'Delayed', due: '2026-08-20' }
  ];

  recentUpdates: UpdateItem[] = [
    { title: 'Concrete pouring completed', time: '2 hours ago', detail: 'Section B of the bridge deck is now complete.' },
    { title: 'Safety audit report uploaded', time: '5 hours ago', detail: 'Site inspection found no major compliance issues.' },
    { title: 'Procurement request approved', time: 'Yesterday', detail: '50 tons of reinforcement bars released for delivery.' }
  ];

  analytics = [
    { label: 'Milestone Completion', value: 72 },
    { label: 'Resource Efficiency', value: 81 },
    { label: 'Workforce Productivity', value: 68 },
    { label: 'On-time Delivery', value: 59 }
  ];
}
