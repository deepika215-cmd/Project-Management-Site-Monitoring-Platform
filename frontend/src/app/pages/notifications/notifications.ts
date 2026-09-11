import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { catchError, finalize, of, Subject, takeUntil, timeout } from 'rxjs';

import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, AppSidebarComponent],
  templateUrl: './notifications.html',
  styleUrls: ['./notifications.css']
})
export class Notifications implements OnInit, OnDestroy {
  notifications: any[] = [];
  loading = false;
  error = '';
  message = '';
  updatingId: number | null = null;
  generating = false;
  deleting = false;
  role = '';
  selectedNotification: any | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private api: Api,
    private cdr: ChangeDetectorRef,
    private router: Router
  ) {
    try {
      this.role = String(JSON.parse(localStorage.getItem('currentUser') || '{}')?.role || '').toUpperCase();
    } catch {
      this.role = '';
    }
  }

  ngOnInit(): void {
    this.load();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  isAdmin(): boolean {
    return this.role === 'ADMIN';
  }

  pageTitle(): string {
    const names: Record<string, string> = {
      ADMIN: 'Admin Notifications',
      PROJECT_MANAGER: 'Project Manager Notifications',
      SITE_ENGINEER: 'Site Engineer Notifications',
      CONTRACTOR: 'Contractor Notifications',
      WORKER: 'Worker Notifications',
      CLIENT: 'Client Notifications'
    };
    return names[this.role] || 'Project Notifications';
  }

  pageSubtitle(): string {
    if (this.isAdmin()) {
      return 'Manage project, task, procurement, attendance, deadline and system alerts.';
    }
    return 'Only alerts relevant to your role, project assignments and responsibilities are shown.';
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.message = '';

    const request$ = this.isAdmin()
      ? this.api.getAllNotifications().pipe(
          timeout({ first: 10000 }),
          catchError(() => this.api.getMyNotifications().pipe(timeout({ first: 8000 })))
        )
      : this.api.getMyNotifications().pipe(timeout({ first: 10000 }));

    request$.pipe(
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
      // Keep a real backend error visible when catchError supplied an empty list.
      // Clear only stale errors after a successful response.
      if (response !== null && !(Array.isArray(response) && response.length === 0 && this.error)) {
        this.error = '';
      }
      this.notifyBadgeRefresh();
    });
  }

  unread(): number {
    return this.notifications.filter(n => String(n?.status || '').toLowerCase() === 'unread').length;
  }

  typeCount(): number {
    return new Set(this.notifications.map(n => this.displayType(n))).size;
  }

  displayType(notification: any): string {
    const value = String(notification?.notification_type || 'SYSTEM')
      .trim()
      .replace(/_/g, ' ')
      .toLowerCase();
    return value.replace(/\b\w/g, c => c.toUpperCase());
  }

  iconFor(notification: any): string {
    const type = String(notification?.notification_type || '').toLowerCase();
    const text = `${notification?.title || ''} ${notification?.message || ''} ${type}`.toLowerCase();
    if (type.includes('procurement') || text.includes('procurement') || text.includes('purchase')) return '📦';
    if (type.includes('attendance') || text.includes('attendance') || text.includes('shift')) return '👷';
    if (type.includes('deadline') || text.includes('deadline') || text.includes('overdue') || text.includes('due today')) return '⏰';
    if (type.includes('task') || text.includes('assigned task') || text.includes('assignment')) return '✅';
    if (type.includes('project') || text.includes('project') || text.includes('milestone') || text.includes('progress')) return '📌';
    if (type.includes('maintenance') || text.includes('maintenance') || text.includes('repair') || text.includes('service')) return '🛠️';
    if (text.includes('budget') || text.includes('cost') || text.includes('payment') || text.includes('invoice')) return '₹';
    if (text.includes('resource') || text.includes('equipment') || text.includes('machinery') || text.includes('crane') || text.includes('generator')) return '🏗️';
    if (text.includes('warning') || text.includes('alert') || text.includes('delay')) return '⚠️';
    return '🔔';
  }

  iconClass(notification: any): string {
    const type = String(notification?.notification_type || '').toLowerCase();
    const text = `${notification?.title || ''} ${notification?.message || ''} ${type}`.toLowerCase();
    if (type.includes('deadline') || text.includes('warning') || text.includes('alert') || text.includes('delay') || text.includes('overdue')) return 'icon-warning';
    if (text.includes('budget') || text.includes('cost') || text.includes('payment') || text.includes('invoice')) return 'icon-budget';
    if (type.includes('procurement')) return 'icon-procurement';
    if (type.includes('attendance') || text.includes('worker') || text.includes('attendance') || text.includes('shift') || text.includes('workforce')) return 'icon-worker';
    if (type.includes('maintenance') || text.includes('maintenance') || text.includes('repair') || text.includes('service')) return 'icon-maintenance';
    if (text.includes('resource') || text.includes('equipment') || text.includes('machinery') || text.includes('crane') || text.includes('generator')) return 'icon-resource';
    return 'icon-info';
  }

  trackByNotification(_: number, item: any): any {
    return item?.id || item?.title || item?.message;
  }

  read(notification: any): void {
    if (!notification?.id || String(notification?.status || '').toLowerCase() === 'read') return;

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
        this.notifyBadgeRefresh();
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((response: any) => {
      if (response?.read_at) notification.read_at = response.read_at;
    });
  }

  markAllRead(): void {
    if (!this.notifications.length || !this.unread()) return;

    const previous = this.notifications.map(n => ({ ...n }));
    this.notifications = this.notifications.map(n => ({ ...n, status: 'Read' }));
    const request$ = this.isAdmin()
      ? this.api.markAllNotificationsRead()
      : this.api.markAllMyNotificationsRead();

    request$.pipe(
      timeout({ first: 10000 }),
      catchError((error: any) => {
        this.notifications = previous;
        this.error = this.errorText(error, 'Unable to mark all notifications as read.');
        return of(null);
      }),
      finalize(() => {
        this.notifyBadgeRefresh();
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe();
  }

  generate(): void {
    if (!this.isAdmin() || this.generating) return;

    this.message = '';
    this.error = '';
    this.generating = true;

    this.api.generateSystemAlerts().pipe(
      timeout({ first: 15000 }),
      catchError((error: any) => {
        this.error = this.errorText(error, 'Unable to generate alerts.');
        return of(null);
      }),
      finalize(() => {
        this.generating = false;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((response: any) => {
      if (!response) return;
      const counts = response?.by_type || {};
      const parts = Object.entries(counts)
        .filter(([, value]) => Number(value) > 0)
        .map(([key, value]) => `${key.replace(/_/g, ' ')}: ${value}`);
      this.message = response?.message || 'Alert scan completed.';
      if (parts.length) this.message += ` (${parts.join(', ')})`;
      this.loadPreservingMessage();
    });
  }

  showDetails(event: Event, notification: any): void {
    event.stopPropagation();
    this.selectedNotification = notification;
    this.read(notification);
  }

  closeDetails(): void {
    this.selectedNotification = null;
  }

  relatedRoute(notification: any): string | null {
    if (notification?.action_url) return String(notification.action_url);

    const text = `${notification?.notification_type || ''} ${notification?.title || ''} ${notification?.message || ''}`.toLowerCase();
    if (text.includes('procurement') || text.includes('purchase')) return this.role === 'WORKER' || this.role === 'CLIENT' ? null : '/procurement';
    if (text.includes('attendance') || text.includes('shift')) return this.role === 'CLIENT' || this.role === 'SITE_ENGINEER' ? null : '/attendance';
    if (text.includes('maintenance') || text.includes('equipment') || text.includes('machinery') || text.includes('resource')) {
      return ['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'].includes(this.role) ? '/resources/operations' : null;
    }
    if (text.includes('budget') || text.includes('cost')) return ['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CLIENT'].includes(this.role) ? '/budget' : null;
    if (notification?.project_id && ['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CONTRACTOR', 'CLIENT'].includes(this.role)) {
      return `/projects/project-details/${notification.project_id}`;
    }
    if (text.includes('project') && this.role !== 'WORKER') return '/projects';
    return null;
  }

  openRelated(event: Event, notification: any): void {
    event.stopPropagation();
    const route = this.relatedRoute(notification);
    if (!route) return;
    this.read(notification);
    this.closeDetails();
    this.router.navigateByUrl(route);
  }

  deleteNotification(event: Event, notification: any): void {
    event.stopPropagation();
    if (!this.isAdmin() || !notification?.id || this.deleting) return;
    if (!window.confirm('Delete this notification?')) return;

    this.deleting = true;
    this.error = '';
    this.api.deleteNotification(notification.id).pipe(
      timeout({ first: 8000 }),
      catchError((error: any) => {
        this.error = this.errorText(error, 'Unable to delete notification.');
        return of(null);
      }),
      finalize(() => {
        this.deleting = false;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((response: any) => {
      if (!response) return;
      this.notifications = this.notifications.filter(n => n.id !== notification.id);
      if (this.selectedNotification?.id === notification.id) this.selectedNotification = null;
      this.message = 'Notification deleted.';
      this.notifyBadgeRefresh();
    });
  }

  private loadPreservingMessage(): void {
    const successMessage = this.message;
    this.loading = true;
    const request$ = this.isAdmin() ? this.api.getAllNotifications() : this.api.getMyNotifications();
    request$.pipe(
      timeout({ first: 10000 }),
      catchError((error: any) => {
        this.error = this.errorText(error, 'Alerts were generated, but the list could not be refreshed.');
        return of([]);
      }),
      finalize(() => {
        this.loading = false;
        this.message = successMessage;
        this.notifyBadgeRefresh();
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((response: any) => {
      this.notifications = this.normalizeList(response);
    });
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
      recipient_user_id: item?.recipient_user_id ?? null,
      notification_type: item?.notification_type || 'SYSTEM',
      project_id: item?.project_id ?? null,
      related_entity_type: item?.related_entity_type || null,
      related_entity_id: item?.related_entity_id ?? null,
      action_url: item?.action_url || null,
      created_at: item?.created_at || item?.createdAt || item?.time || '',
      read_at: item?.read_at || null
    }));
  }

  private notifyBadgeRefresh(): void {
    window.dispatchEvent(new CustomEvent('buildtrack-notifications-changed'));
  }

  private errorText(error: any, fallback: string): string {
    const detail = error?.error?.detail;
    if (typeof detail === 'string' && detail.trim()) return detail;
    if (Array.isArray(detail)) {
      return detail.map((item: any) => item?.msg || item?.message || JSON.stringify(item)).join(' | ');
    }
    if (error?.status === 0) {
      return 'Backend is not responding. Start FastAPI on http://localhost:8000 and refresh this page.';
    }
    return fallback;
  }
}
