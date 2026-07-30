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

interface AttendanceRecord {
  date: string;
  status: string;
  timeIn: string;
  timeOut: string;
}

@Component({
  selector: 'app-worker-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './worker-dashboard.component.html',
  styleUrl: './worker-dashboard.component.scss'
})
export class WorkerDashboardComponent {
  sidebar: SidebarItem[] = [
    { label: 'Dashboard', icon: '📊', active: true },
    { label: 'My Tasks', icon: '🛠️' },
    { label: 'Attendance', icon: '✅' },
    { label: 'Shift Schedule', icon: '🕒' },
    { label: 'Profile', icon: '👤' },
    { label: 'Logout', icon: '⇦' }
  ];

  tasks: TaskItem[] = [
    { title: 'Inspect foundation rebar', project: 'North Ridge Highway', due: 'Today', status: 'In progress' },
    { title: 'Prepare formwork', project: 'Downtown Plaza', due: 'Tomorrow', status: 'Pending' },
    { title: 'Check concrete mix ratio', project: 'East Side Waterline', due: 'Fri', status: 'Completed' }
  ];

  attendance: AttendanceRecord[] = [
    { date: '2026-08-22', status: 'Present', timeIn: '07:05', timeOut: '16:40' },
    { date: '2026-08-21', status: 'Present', timeIn: '07:10', timeOut: '16:45' },
    { date: '2026-08-20', status: 'Absent', timeIn: '-', timeOut: '-' }
  ];

  shiftSchedule = [
    { shift: 'Morning', time: '07:00 - 15:00', location: 'North Ridge Highway' },
    { shift: 'Evening', time: '15:00 - 23:00', location: 'Downtown Plaza' }
  ];
}
