import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

<<<<<<< HEAD
interface Notification {

  title: string;
  message: string;
  time: string;
  type: string;

=======
interface NotificationItem {
  icon: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'Info' | 'Success' | 'Warning' | 'Critical';
>>>>>>> 60d61182f3bcd948dd0338842f23ae837bca1e0b
}

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.html',
  styleUrls: ['./notifications.css'],
})
export class Notifications {
<<<<<<< HEAD

  notifications: Notification[] = [

    {
      title: 'New Project Assigned',
      message: 'Green Valley Apartments has been assigned to you.',
      time: '2 minutes ago',
      type: 'info'
    },

    {
      title: 'Milestone Updated',
      message: 'Foundation milestone completed.',
      time: '1 hour ago',
      type: 'warning'
    },

    {
      title: 'Project Completed',
      message: 'Industrial Warehouse completed successfully.',
      time: 'Yesterday',
      type: 'success'
    },

    {
      title: 'Material Request Approved',
      message: 'Your cement request has been approved.',
      time: '2 days ago',
      type: 'info'
    }

  ];

}
=======
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

>>>>>>> 60d61182f3bcd948dd0338842f23ae837bca1e0b
