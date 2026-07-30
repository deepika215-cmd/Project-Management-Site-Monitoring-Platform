import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface SidebarItem {
  label: string;
  icon: string;
  active?: boolean;
}

interface TaskItem {
  title: string;
  project: string;
  due: string;
  status: string;
}

interface WorkerItem {
  name: string;
  role: string;
  status: string;
}

interface AttendanceRecord {
  date: string;
  present: number;
  absent: number;
}

interface ShiftItem {
  shift: string;
  time: string;
  site: string;
}

interface NotificationItem {
  title: string;
  detail: string;
  time: string;
}

@Component({
  selector: 'app-contractor-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contractor-dashboard.component.html',
  styleUrl: './contractor-dashboard.component.scss'
})
export class ContractorDashboardComponent {
  sidebar: SidebarItem[] = [
    { label: 'Dashboard', icon: '📊', active: true },
    { label: 'Assigned Tasks', icon: '🛠️' },
    { label: 'Worker List', icon: '👥' },
    { label: 'Attendance', icon: '✅' },
    { label: 'Work Progress', icon: '📈' },
    { label: 'Shift Schedule', icon: '🕒' },
    { label: 'Notifications', icon: '🔔' },
    { label: 'Profile', icon: '👤' }
  ];

  tasks: TaskItem[] = [
    { title: 'Complete beam installation', project: 'River Bridge Expansion', due: 'Today', status: 'In progress' },
    { title: 'Verify concrete pour', project: 'Metro Station Upgrade', due: 'Tomorrow', status: 'Pending' },
    { title: 'Review safety checks', project: 'Downtown Plaza', due: 'Friday', status: 'Completed' }
  ];

  workers: WorkerItem[] = [
    { name: 'Suresh Kumar', role: 'Foreman', status: 'On site' },
    { name: 'Ravi Patel', role: 'Steel Fixer', status: 'Assigned' },
    { name: 'Meena Sharma', role: 'Mason', status: 'On break' }
  ];

  attendanceSummary: AttendanceRecord[] = [
    { date: '2026-08-22', present: 32, absent: 3 },
    { date: '2026-08-21', present: 30, absent: 5 },
    { date: '2026-08-20', present: 28, absent: 7 }
  ];

  progressValue = 76;

  shifts: ShiftItem[] = [
    { shift: 'Morning', time: '07:00 - 15:00', site: 'River Bridge Expansion' },
    { shift: 'Evening', time: '15:00 - 23:00', site: 'Metro Station Upgrade' }
  ];

  notifications: NotificationItem[] = [
    { title: 'Worker assignment updated', detail: 'Ravi moved to Metro Station.', time: '1h ago' },
    { title: 'Attendance sheet due', detail: 'Submit daily attendance before 6 PM.', time: '3h ago' },
    { title: 'Safety tool inspection', detail: 'Schedule equipment check for Thursday.', time: 'Yesterday' }
  ];
}
