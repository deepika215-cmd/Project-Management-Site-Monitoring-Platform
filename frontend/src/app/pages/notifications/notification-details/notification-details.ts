import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  ActivatedRoute,
  Router
} from '@angular/router';

import {
  NotificationItem,
  NotificationService
} from '../notification.service';

@Component({
  selector: 'app-notification-details',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './notification-details.html',
  styleUrl: './notification-details.css'
})
export class NotificationDetails implements OnInit {

  private route = inject(
    ActivatedRoute
  );

  private router = inject(
    Router
  );

  private notificationService = inject(
    NotificationService
  );

  notification:
    NotificationItem | null = null;

  loading = true;

  error = '';

  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {

    const idParam =
      this.route.snapshot.paramMap.get('id');

    console.log(
      'Notification ID from URL:',
      idParam
    );

    const id =
      Number(idParam);

    if (
      !idParam ||
      Number.isNaN(id) ||
      id <= 0
    ) {

      this.error =
        'Invalid notification ID.';

      this.loading = false;

      return;
    }

    this.loadNotification(id);
  }

  // =====================================================
  // LOAD NOTIFICATION
  // =====================================================

  loadNotification(
    id: number
  ): void {

    this.loading = true;
    this.error = '';

    console.log(
      'Loading notification:',
      id
    );

    this.notificationService
      .getNotification(id)
      .subscribe({

        next: (
          notification: NotificationItem
        ) => {

          console.log(
            'Notification API response:',
            notification
          );

          this.notification =
            notification;

          this.loading = false;

          // Automatically mark unread
          // notification as read
          if (
            !this.notificationService
              .isRead(notification)
          ) {

            this.markAsRead();
          }
        },

        error: (error: any) => {

          console.error(
            'Notification details error:',
            error
          );

          this.notification = null;

          this.error =
            error?.error?.detail ||
            error?.error?.message ||
            'Unable to load notification.';

          this.loading = false;
        }
      });
  }

  // =====================================================
  // MARK AS READ
  // =====================================================

  markAsRead(): void {

    if (!this.notification) {
      return;
    }

    const current =
      this.notification;

    this.notificationService
      .markAsRead(current)
      .subscribe({

        next: (
          response: NotificationItem
        ) => {

          console.log(
            'Marked as read:',
            response
          );

          if (this.notification) {

            this.notification.status =
              'Read';

            this.notification.is_read =
              true;

            this.notification.read =
              true;

            this.notification.read_at =
              new Date().toISOString();
          }
        },

        error: (error: any) => {

          console.error(
            'Unable to mark notification as read:',
            error
          );

          // Do not block details page
        }
      });
  }

  // =====================================================
  // MARK AS UNREAD
  // =====================================================

  markAsUnread(): void {

    if (!this.notification) {
      return;
    }

    const current =
      this.notification;

    this.notificationService
      .markAsUnread(current)
      .subscribe({

        next: (
          response: NotificationItem
        ) => {

          console.log(
            'Marked as unread:',
            response
          );

          if (this.notification) {

            this.notification.status =
              'Unread';

            this.notification.is_read =
              false;

            this.notification.read =
              false;

            this.notification.read_at =
              null;
          }
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
  // BACK
  // =====================================================

  goBack(): void {

    this.router.navigate([
      '/notifications'
    ]);
  }

  // =====================================================
  // RELATED INFORMATION
  // =====================================================

  openRelatedInformation(): void {

    if (!this.notification) {
      return;
    }

    const notification =
      this.notification;

    const url =
      notification.action_url ||
      notification.link;

    if (url) {

      this.router.navigateByUrl(
        url
      );

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

    if (notification.milestone_id) {

      this.router.navigate([
        '/milestones',
        notification.milestone_id
      ]);

      return;
    }
  }

  // =====================================================
  // TITLE
  // =====================================================

  getTitle(): string {

    if (!this.notification) {

      return 'Notification';
    }

    return this.notificationService
      .getTitle(
        this.notification
      );
  }

  // =====================================================
  // MESSAGE
  // =====================================================

  getMessage(): string {

    if (!this.notification) {

      return '';
    }

    return this.notificationService
      .getMessage(
        this.notification
      );
  }

  // =====================================================
  // TYPE
  // =====================================================

  getType(): string {

    if (!this.notification) {

      return 'SYSTEM';
    }

    return this.notificationService
      .getType(
        this.notification
      );
  }

  // =====================================================
  // DATE
  // =====================================================

  getDate(): string {

    if (!this.notification) {

      return '';
    }

    return this.notificationService
      .getDate(
        this.notification
      );
  }

  // =====================================================
  // READ STATUS
  // =====================================================

  isRead(): boolean {

    if (!this.notification) {

      return false;
    }

    return this.notificationService
      .isRead(
        this.notification
      );
  }
}