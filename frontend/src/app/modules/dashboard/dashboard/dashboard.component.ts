import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

interface NavItem {
  label: string;
  icon: string;
  active?: boolean;
}

interface StatCard {
  title: string;
  value: string;
  change: string;
  accent: string;
}

interface ActivityItem {
  title: string;
  time: string;
  detail: string;
}

interface NotificationItem {
  title: string;
  detail: string;
  priority: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  navItems: NavItem[] = [
    { label: 'Dashboard', icon: '◉', active: true },
    { label: 'User Management', icon: '◌' },
    { label: 'Project Management', icon: '◌' },
    { label: 'Workforce Management', icon: '◌' },
    { label: 'Resource Management', icon: '◌' },
    { label: 'Material & Inventory Management', icon: '◌' },
    { label: 'Procurement Management', icon: '◌' },
    { label: 'Budget Management', icon: '◌' },
    { label: 'Reports', icon: '◌' },
    { label: 'Notifications', icon: '◌' },
    { label: 'Analytics', icon: '◌' },
    { label: 'Settings', icon: '◌' },
    { label: 'Logout', icon: '⇢' }
  ];

  stats: StatCard[] = [
    { title: 'Total Projects', value: '24', change: '+4 this month', accent: 'blue' },
    { title: 'Active Projects', value: '12', change: '3 nearing deadline', accent: 'green' },
    { title: 'Total Users', value: '86', change: '+8 new accounts', accent: 'purple' },
    { title: 'Active Workers', value: '41', change: 'On-site today', accent: 'orange' },
    { title: 'Ongoing Procurement Requests', value: '9', change: '2 pending approval', accent: 'teal' },
    { title: 'Budget Utilization', value: '78%', change: 'Within target', accent: 'red' }
  ];

  activities: ActivityItem[] = [
    { title: 'Site inspection completed', time: '10 min ago', detail: 'Bridge construction site is now fully reviewed.' },
    { title: 'Procurement approved', time: '45 min ago', detail: 'Steel delivery request approved for the next phase.' },
    { title: 'Budget threshold reached', time: '1 hr ago', detail: 'Quarterly spend is now 78% of projected budget.' }
  ];

  notifications: NotificationItem[] = [
    { title: 'Material stock low', detail: 'Cement inventory is below the minimum threshold.', priority: 'High' },
    { title: 'Worker shift update', detail: 'Three crews need reassignment for the afternoon.', priority: 'Medium' },
    { title: 'Report due tomorrow', detail: 'Monthly productivity report is awaiting approval.', priority: 'Low' }
  ];

  projectStatus = [
    { name: 'Planning', value: 65 },
    { name: 'Design', value: 82 },
    { name: 'Execution', value: 74 },
    { name: 'Monitoring', value: 58 },
    { name: 'Closure', value: 39 }
  ];
}
