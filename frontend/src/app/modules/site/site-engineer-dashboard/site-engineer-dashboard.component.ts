import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface SidebarItem {
  label: string;
  icon: string;
  active?: boolean;
}

interface ProgressProject {
  name: string;
  progress: number;
  due: string;
  status: string;
}

interface DailyReport {
  date: string;
  summary: string;
  progress: string;
}

interface EquipmentStatus {
  name: string;
  status: string;
  availability: string;
}

interface ResourceAvailability {
  type: string;
  available: string;
  usage: string;
}

interface ActivityLog {
  time: string;
  activity: string;
  project: string;
}

interface NotificationItem {
  title: string;
  detail: string;
  time: string;
}

@Component({
  selector: 'app-site-engineer-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './site-engineer-dashboard.component.html',
  styleUrl: './site-engineer-dashboard.component.scss'
})
export class SiteEngineerDashboardComponent {
  sidebar: SidebarItem[] = [
    { label: 'Dashboard', icon: '📊', active: true },
    { label: 'Assigned Projects', icon: '📁' },
    { label: 'Daily Progress Reports', icon: '📝' },
    { label: 'Weekly Reports', icon: '📅' },
    { label: 'Site Activity Logs', icon: '🧾' },
    { label: 'Equipment Status', icon: '🚜' },
    { label: 'Resource Availability', icon: '🧰' },
    { label: 'Notifications', icon: '🔔' },
    { label: 'Profile', icon: '👤' }
  ];

  projects: ProgressProject[] = [
    { name: 'North Ridge Highway', progress: 68, due: '2026-10-12', status: 'On schedule' },
    { name: 'East Side Waterline', progress: 52, due: '2026-09-25', status: 'Needs review' },
    { name: 'Downtown Plaza', progress: 85, due: '2026-11-05', status: 'Ahead of schedule' }
  ];

  dailyReports: DailyReport[] = [
    { date: '2026-08-22', summary: 'Foundation poured for Sector 4', progress: '5% increase' },
    { date: '2026-08-21', summary: 'Safety inspection completed', progress: 'No delays' },
    { date: '2026-08-20', summary: 'Material delivery received', progress: 'Procurement on track' }
  ];

  equipment: EquipmentStatus[] = [
    { name: 'Crane A12', status: 'Operational', availability: '92%' },
    { name: 'Bulldozer B3', status: 'Maintenance due', availability: '72%' },
    { name: 'Concrete Mixer C7', status: 'Operational', availability: '88%' }
  ];

  resources: ResourceAvailability[] = [
    { type: 'Cement bags', available: '1,240', usage: '76%' },
    { type: 'Rebar', available: '640 tons', usage: '61%' },
    { type: 'Labor crew', available: '48 workers', usage: '84%' }
  ];

  activityLogs: ActivityLog[] = [
    { time: '08:40', activity: 'Concrete pour started at Sector 2', project: 'North Ridge Highway' },
    { time: '10:15', activity: 'Safety barrier installed', project: 'Downtown Plaza' },
    { time: '12:30', activity: 'Material handoff completed', project: 'East Side Waterline' }
  ];

  notifications: NotificationItem[] = [
    { title: 'Equipment check pending', detail: 'Schedule inspection for Crane A12.', time: '2 hours ago' },
    { title: 'Weekly report due', detail: 'Compile site update for Friday review.', time: 'Yesterday' },
    { title: 'Resource allocation change', detail: 'Additional labour requested for East Side Waterline.', time: 'Today' }
  ];
}
