import { Component } from '@angular/core';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-site-engineer-notifications',
  imports: [AppSidebarComponent],
  templateUrl: './site-engineer-notifications.html',
  styleUrl: './site-engineer-notifications.css',
})
export class SiteEngineerNotifications {
  notifications: any[] = [];
  loading = false;
  error = '';

  constructor() {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.loading = true;
    this.error = '';

    // Notifications API integration can be connected here
    // when the backend endpoint is available.
    this.notifications = [];

    this.loading = false;
  }
}