import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { catchError, finalize, of, Subject, takeUntil, timeout } from 'rxjs';

import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-worker-notifications',
  standalone: true,
  imports: [CommonModule, AppSidebarComponent],
  templateUrl: './worker-notifications.html',
  styleUrls: ['./worker-notifications.css']
})
export class WorkerNotifications implements OnInit, OnDestroy {
  notifications: any[] = [];
  loading = false;
  error = '';
  message = '';
  updatingId: number | null = null;
  generating = false;

  private destroy$ = new Subject<void>();

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.load();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.message = '';

    this.api.getMyNotifications().pipe(timeout({ first: 10000 })).pipe(
      catchError((error: any) => {
        this.error = this.errorText(error, 'Unable to load notifications.');
        return of([]);
      }),
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((response: any) => {
      this.notifications = this.normalizeList(response);
    });
  }

  unread(): number {
    return this.notifications.filter(n => String(n?.status || '').toLowerCase() === 'unread').length;
  }

  iconFor(notification: any): string {
    const text = `${notification?.title || ''} ${notification?.message || ''}`.toLowerCase();
    if (text.includes('budget') || text.includes('cost') || text.includes('payment') || text.includes('invoice')) {
      return '₹';
    }
    if (text.includes('resource') || text.includes('equipment') || text.includes('machinery') || text.includes('crane') || text.includes('generator')) {
      return '🏗️';
    }
    if (text.includes('worker') || text.includes('attendance') || text.includes('shift') || text.includes('workforce')) {
      return '👷';
    }
    if (text.includes('project') || text.includes('milestone') || text.includes('progress')) {
      return '📌';
    }
    if (text.includes('maintenance') || text.includes('repair') || text.includes('service')) {
      return '🛠️';
    }
    if (text.includes('warning') || text.includes('alert') || text.includes('delay') || text.includes('overdue')) {
      return '⚠️';
    }
    if (text.includes('client') || text.includes('approval')) {
      return '🤝';
    }
    return '🔔';
  }

  iconClass(notification: any): string {
    const text = `${notification?.title || ''} ${notification?.message || ''}`.toLowerCase();
    if (text.includes('warning') || text.includes('alert') || text.includes('delay') || text.includes('overdue')) {
      return 'icon-warning';
    }
    if (text.includes('budget') || text.includes('cost') || text.includes('payment') || text.includes('invoice')) {
      return 'icon-budget';
    }
    if (text.includes('resource') || text.includes('equipment') || text.includes('machinery') || text.includes('crane') || text.includes('generator')) {
      return 'icon-resource';
    }
    if (text.includes('worker') || text.includes('attendance') || text.includes('shift') || text.includes('workforce')) {
      return 'icon-worker';
    }
    if (text.includes('maintenance') || text.includes('repair') || text.includes('service')) {
      return 'icon-maintenance';
    }
    return 'icon-info';
  }

  trackByNotification(_: number, item: any): any {
    return item?.id || item?.title || item?.message;
  }

  read(notification: any): void {
    if (!notification?.id || String(notification?.status || '').toLowerCase() === 'read') {
      return;
    }

    const previousStatus = notification.status;
    notification.status = 'Read';
    this.updatingId = notification.id;
    this.error = '';

    this.api.markNotificationRead(notification.id).pipe(
      timeout({ first: 8000 }),
      catchError((error: any) => {
        notification.status = previousStatus;
        this.error = this.errorText(error, 'Unable to mark notification as read.');
        return of(null);
      }),
      finalize(() => {
        this.updatingId = null;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe();
  }

  markAllRead(): void {
    if (!this.notifications.length) {
      return;
    }

    const previous = this.notifications.map(n => ({ ...n }));
    this.notifications = this.notifications.map(n => ({ ...n, status: 'Read' }));

    this.api.markAllMyNotificationsRead().pipe(
      timeout({ first: 10000 }),
      catchError((error: any) => {
        this.notifications = previous;
        this.error = this.errorText(error, 'Unable to mark all notifications as read.');
        return of(null);
      }),
      finalize(() => this.cdr.detectChanges()),
      takeUntil(this.destroy$)
    ).subscribe();
  }

  private normalizeList(response: any): any[] {
    const raw = Array.isArray(response)
      ? response
      : Array.isArray(response?.notifications)
        ? response.notifications
        : Array.isArray(response?.data)
          ? response.data
          : [];

    return raw.map((item: any) => ({
      ...item,
      title: item?.title || item?.subject || 'Notification',
      message: item?.message || item?.description || '',
      status: item?.status || 'Unread',
      recipient: item?.recipient || '',
      created_at: item?.created_at || item?.createdAt || item?.time || ''
    }));
  }

  private errorText(error: any, fallback: string): string {
    const detail = error?.error?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item: any) => item?.msg || item?.message || JSON.stringify(item)).join(' | ');
    }
    if (error?.status === 0) {
      return 'Backend is not responding. Start FastAPI on http://localhost:8000 and refresh this page.';
    }
    return fallback;
  }
}
