import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface Notification {

  title: string;
  message: string;
  time: string;
  type: string;

}

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.html',
  styleUrl: './notifications.css',
})
export class Notifications {

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