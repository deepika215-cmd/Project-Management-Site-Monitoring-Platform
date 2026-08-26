import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

interface Notification {
  title: string;
  message: string;
  time: string;
}

@Component({
  selector: 'app-admin-notifications',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    AppSidebarComponent
  ],
  templateUrl: './admin-notifications.html',
  styleUrls: ['./admin-notifications.css']
})
export class AdminNotifications {

  notifications: Notification[] = [

    {
      title: 'New Project Assigned',
      message: 'Green Valley Apartments has been assigned.',
      time: '2 minutes ago'
    },

    {
      title: 'Milestone Updated',
      message: 'Foundation milestone completed.',
      time: '1 hour ago'
    },

    {
      title: 'Material Request Approved',
      message: '200 bags of cement approved.',
      time: 'Yesterday'
    },

    {
      title: 'Project Completed',
      message: 'Industrial Warehouse completed successfully.',
      time: '2 days ago'
    }

  ];

}