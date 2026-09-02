import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { AppSidebarComponent } from '../../shared/app-sidebar.component';

import {
  NotificationItem,
  NotificationService
} from './notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [
    CommonModule,
    AppSidebarComponent
  ],
  templateUrl: './notifications.html',
  styleUrl: './notifications.css'
})
export class Notifications implements OnInit {

  private notificationService =
    inject(NotificationService);

  private router =
    inject(Router);

  notifications: NotificationItem[] = [];

  loading = true;
  refreshing = false;
  error = '';

  selectedFilter = 'ALL';

  unreadCount = 0;

  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {
    this.loadNotifications();
  }

  // =====================================================
  // LOAD
  // =====================================================

  loadNotifications(): void {

    this.loading = true;
    this.error = '';

    this.notificationService
      .getNotifications()
      .subscribe({

        next: (notifications: NotificationItem[]) => {

          this.notifications =
            Array.isArray(notifications)
              ? notifications
              : [];

          this.updateUnreadCount();

          this.loading = false;
        },

        error: (error: any) => {

          console.error(
            'Notification loading error:',
            error
          );

          this.error =
            error?.error?.detail ||
            error?.error?.message ||
            'Unable to load notifications.';

          this.loading = false;
        }
      });
  }

  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {

    this.refreshing = true;
    this.error = '';

    this.notificationService
      .getNotifications()
      .subscribe({

        next: (notifications: NotificationItem[]) => {

          this.notifications =
            Array.isArray(notifications)
              ? notifications
              : [];

          this.updateUnreadCount();

          this.refreshing = false;
        },

        error: (error: any) => {

          console.error(
            'Notification refresh error:',
            error
          );

          this.refreshing = false;

          this.error =
            error?.error?.detail ||
            error?.error?.message ||
            'Unable to refresh notifications.';
        }
      });
  }

  // =====================================================
  // UNREAD COUNT
  // =====================================================

  updateUnreadCount(): void {

    this.unreadCount =
      this.notificationService
        .getUnreadCount(
          this.notifications
        );
  }

  // =====================================================
  // HELPERS
  // =====================================================

  isRead(
    notification: NotificationItem
  ): boolean {

    return this.notificationService
      .isRead(notification);
  }

  getTitle(
    notification: NotificationItem
  ): string {

    return this.notificationService
      .getTitle(notification);
  }

  getMessage(
    notification: NotificationItem
  ): string {

    return this.notificationService
      .getMessage(notification);
  }

  getType(
    notification: NotificationItem
  ): string {

    return this.notificationService
      .getType(notification);
  }

  getDate(
    notification: NotificationItem
  ): string {

    return this.notificationService
      .getDate(notification);
  }

  // =====================================================
  // FILTER
  // =====================================================

  get filteredNotifications(): NotificationItem[] {

    if (this.selectedFilter === 'UNREAD') {

      return this.notifications.filter(
        notification => !this.isRead(notification)
      );
    }

    if (this.selectedFilter === 'READ') {

      return this.notifications.filter(
        notification => this.isRead(notification)
      );
    }

    return this.notifications;
  }

  setFilter(filter: string): void {
    this.selectedFilter = filter;
  }

  // =====================================================
  // OPEN NOTIFICATION
  // =====================================================

  openNotification(
    notification: NotificationItem
  ): void {

    if (!this.isRead(notification)) {

      this.notificationService
        .markAsRead(notification)
        .subscribe({

          next: () => {

            notification.is_read = true;
            notification.read = true;
            notification['read_at'] =
              new Date().toISOString();

            this.updateUnreadCount();
          },

          error: (error: any) => {

            console.error(
              'Unable to mark notification as read:',
              error
            );
          }
        });
    }

    this.router.navigate([
      '/notification-details',
      notification.id
    ]);
  }

  // =====================================================
  // MARK AS READ
  // =====================================================

  markAsRead(
    event: Event,
    notification: NotificationItem
  ): void {

    event.stopPropagation();

    if (this.isRead(notification)) {
      return;
    }

    this.notificationService
      .markAsRead(notification)
      .subscribe({

        next: () => {

          notification.is_read = true;
          notification.read = true;
          notification['read_at'] =
            new Date().toISOString();

          this.updateUnreadCount();
        },

        error: (error: any) => {

          console.error(
            'Unable to mark notification as read:',
            error
          );
        }
      });
  }

  // =====================================================
  // MARK AS UNREAD
  // =====================================================

  markAsUnread(
    event: Event,
    notification: NotificationItem
  ): void {

    event.stopPropagation();

    if (!this.isRead(notification)) {
      return;
    }

    this.notificationService
      .markAsUnread(notification)
      .subscribe({

        next: () => {

          notification.is_read = false;
          notification.read = false;
          notification['read_at'] = null;

          this.updateUnreadCount();
        },

        error: (error: any) => {

          console.error(
            'Unable to mark notification as unread:',
            error
          );
        }
      });
  }

  // =====================================================
  // RELATED INFORMATION
  // =====================================================

  goToRelatedInformation(
    event: Event,
    notification: NotificationItem
  ): void {

    event.stopPropagation();

    if (!this.isRead(notification)) {

      this.notificationService
        .markAsRead(notification)
        .subscribe({

          next: () => {

            notification.is_read = true;
            notification.read = true;
            notification['read_at'] =
              new Date().toISOString();

            this.updateUnreadCount();
          },

          error: (error: any) => {

            console.error(
              'Unable to mark notification as read:',
              error
            );
          }
        });
    }

    const url =
      notification['action_url'] ||
      notification['link'];

    if (url) {

      this.router.navigateByUrl(url);

      return;
    }

    if (notification.project_id) {

      this.router.navigate([
        '/projects',
        notification.project_id
      ]);

      return;
    }

    if (notification.task_id) {

      this.router.navigate([
        '/tasks',
        notification.task_id
      ]);

      return;
    }

    if (notification['milestone_id']) {

      this.router.navigate([
        '/milestones',
        notification['milestone_id']
      ]);

      return;
    }

    this.router.navigate([
      '/notification-details',
      notification.id
    ]);
  }

  // =====================================================
  // TRACK BY
  // =====================================================

  trackByNotification(
    index: number,
    notification: NotificationItem
  ): number {

    return notification.id || index;
  }
}