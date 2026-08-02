import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface NotificationItem {
  icon: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'Info' | 'Success' | 'Warning' | 'Critical';
}

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.html',
  styleUrls: ['./notifications.css'],
})
export class Notifications {
  notifications: NotificationItem[] = [
    {
      icon: '🚧',
      title: 'New safety inspection scheduled',
      description: 'A site safety inspection is scheduled for tomorrow at 10:00 AM.',
      timestamp: '12 minutes ago',
      status: 'Info'
    },
    {
      icon: '📦',
      title: 'Material delivery delayed',
      description: 'The steel beam shipment has been delayed by 2 days.',
      timestamp: '35 minutes ago',
      status: 'Warning'
    },
    {
      icon: '✅',
      title: 'Milestone achieved',
      description: 'Foundation work completed ahead of schedule.',
      timestamp: '1 hour ago',
      status: 'Success'
    },
    {
      icon: '⚠️',
      title: 'Overdue permit renewal',
      description: 'Permit renewal is overdue for the East wing project.',
      timestamp: '2 hours ago',
      status: 'Critical'
    }
  ];
}

