import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { Api } from '../../services/api';

export interface NotificationItem {
  id: number;

  title?: string;
  message?: string;
  recipient?: string;
  status?: string;

  // Optional fields - future backend compatibility
  description?: string;
  type?: string;
  notification_type?: string;
  created_at?: string;
  time?: string;

  is_read?: boolean;
  read?: boolean;
  read_at?: string | null;

  user_id?: number;
  project_id?: number;
  task_id?: number;
  milestone_id?: number;

  action_url?: string;
  link?: string;

  [key: string]: any;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {

  constructor(
    private api: Api
  ) {}

  // =====================================================
  // GET ALL NOTIFICATIONS
  // =====================================================

  getNotifications(): Observable<NotificationItem[]> {

    return this.api
      .getNotifications()
      .pipe(
        map((response: any) => {

          if (Array.isArray(response)) {
            return response;
          }

          return [];
        })
      );
  }

  // =====================================================
  // GET SINGLE NOTIFICATION
  // =====================================================

  getNotification(
    id: number
  ): Observable<NotificationItem> {

    return this.api.getNotification(id);
  }

  // =====================================================
  // CREATE
  // =====================================================

  createNotification(
    notification: any
  ): Observable<NotificationItem> {

    return this.api.createNotification(
      notification
    );
  }

  // =====================================================
  // UPDATE
  // =====================================================

  updateNotification(
    id: number,
    notification: any
  ): Observable<NotificationItem> {

    return this.api.updateNotification(
      id,
      notification
    );
  }

  // =====================================================
  // DELETE
  // =====================================================

  deleteNotification(
    id: number
  ): Observable<any> {

    return this.api.deleteNotification(id);
  }

  // =====================================================
  // CHECK READ STATUS
  // =====================================================

  isRead(
    notification: NotificationItem
  ): boolean {

    // Backend uses status
    if (
      notification.status !== undefined &&
      notification.status !== null
    ) {

      return String(
        notification.status
      ).toLowerCase() === 'read';
    }

    // Fallback for old response format
    return (
      notification.is_read === true ||
      notification.read === true
    );
  }

  // =====================================================
  // TITLE
  // =====================================================

  getTitle(
    notification: NotificationItem
  ): string {

    return (
      notification.title ||
      notification['subject'] ||
      'Notification'
    );
  }

  // =====================================================
  // MESSAGE
  // =====================================================

  getMessage(
    notification: NotificationItem
  ): string {

    return (
      notification.message ||
      notification.description ||
      notification['body'] ||
      'No notification message available.'
    );
  }

  // =====================================================
  // TYPE
  // =====================================================

  getType(
    notification: NotificationItem
  ): string {

    return String(
      notification.type ||
      notification.notification_type ||
      notification['category'] ||
      'SYSTEM'
    ).toUpperCase();
  }

  // =====================================================
  // DATE
  // =====================================================

  getDate(
    notification: NotificationItem
  ): string {

    const date =
      notification.created_at ||
      notification.time;

    if (!date) {

      return '';
    }

    try {

      return new Date(date)
        .toLocaleString();

    } catch {

      return String(date);
    }
  }

  // =====================================================
  // MARK AS READ
  // =====================================================

  markAsRead(
    notification: NotificationItem
  ): Observable<NotificationItem> {

    return this.api.updateNotification(
      notification.id,
      {
        title: notification.title,
        message: notification.message,
        recipient: notification.recipient,
        status: 'Read'
      }
    );
  }

  // =====================================================
  // MARK AS UNREAD
  // =====================================================

  markAsUnread(
    notification: NotificationItem
  ): Observable<NotificationItem> {

    return this.api.updateNotification(
      notification.id,
      {
        title: notification.title,
        message: notification.message,
        recipient: notification.recipient,
        status: 'Unread'
      }
    );
  }

  // =====================================================
  // UNREAD COUNT
  // =====================================================

  getUnreadCount(
    notifications: NotificationItem[]
  ): number {

    return notifications.filter(
      notification =>
        !this.isRead(notification)
    ).length;
  }
}