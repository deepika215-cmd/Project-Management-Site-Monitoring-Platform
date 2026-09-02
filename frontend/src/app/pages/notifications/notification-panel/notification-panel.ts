import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import {
  NotificationItem,
  NotificationService
} from '../notification.service';

@Component({
  selector: 'app-notification-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notification-panel.html',
  styleUrl: './notification-panel.css'
})
export class NotificationPanel implements OnInit {

  private notificationService =
    inject(NotificationService);

  private router =
    inject(Router);

  notifications: NotificationItem[] = [];

  unreadCount = 0;

  loading = true;

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {

    this.loading = true;

    this.notificationService
      .getNotifications()
      .subscribe({

        next: (
          notifications: NotificationItem[]
        ) => {

          this.notifications =
            Array.isArray(notifications)
              ? notifications
              : [];

          this.unreadCount =
            this.notificationService
              .getUnreadCount(
                this.notifications
              );

          this.loading = false;
        },

        error: (error: any) => {

          console.error(
            'Notification panel error:',
            error
          );

          this.loading = false;
        }
      });
  }

  get recentNotifications(): NotificationItem[] {

    return this.notifications.slice(0, 5);
  }

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

            this.unreadCount =
              this.notificationService
                .getUnreadCount(
                  this.notifications
                );
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

  openAll(): void {

    this.router.navigate([
      '/notifications'
    ]);
  }

  trackByNotification(
    index: number,
    notification: NotificationItem
  ): number {

    return notification.id || index;
  }
}