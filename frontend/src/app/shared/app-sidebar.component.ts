import { CommonModule } from '@angular/common';
import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { catchError, interval, of, Subject, takeUntil, timeout } from 'rxjs';

import { Api } from '../services/api';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './app-sidebar.component.html',
  styleUrl: './app-sidebar.component.css'
})
export class AppSidebarComponent implements OnInit, OnDestroy {
  @Input() active = '';

  role = '';
  dashboardLink = '/project-manager-dashboard';
  notificationLink = '/notifications';
  unreadCount = 0;
  recentNotifications: any[] = [];
  notificationPanelOpen = false;

  private destroy$ = new Subject<void>();
  private readonly notificationChangedHandler = () => this.loadNotificationPreview();

  constructor(private router: Router, private api: Api) {}

  ngOnInit(): void {
    this.syncUser();
    this.loadNotificationPreview();

    // Keep the unread indicator fresh without forcing the user to open the page.
    interval(30000).pipe(takeUntil(this.destroy$)).subscribe(() => this.loadNotificationPreview());
    window.addEventListener('buildtrack-notifications-changed', this.notificationChangedHandler);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    window.removeEventListener('buildtrack-notifications-changed', this.notificationChangedHandler);
  }

  private syncUser(): void {
    try {
      this.role = String(JSON.parse(localStorage.getItem('currentUser') || '{}')?.role || '').toUpperCase();
    } catch {
      this.role = '';
    }

    const dashboards: Record<string, string> = {
      ADMIN: '/admin-dashboard',
      PROJECT_MANAGER: '/project-manager-dashboard',
      SITE_ENGINEER: '/site-engineer-dashboard',
      CONTRACTOR: '/contractor-dashboard',
      WORKER: '/worker-dashboard',
      CLIENT: '/client-dashboard'
    };

    this.dashboardLink = dashboards[this.role] || '/project-manager-dashboard';
    this.notificationLink = '/notifications';
  }

  private loadNotificationPreview(): void {
    if (!localStorage.getItem('token')) {
      this.unreadCount = 0;
      this.recentNotifications = [];
      return;
    }

    this.api.getMyNotifications().pipe(
      timeout({ first: 8000 }),
      catchError(() => of([])),
      takeUntil(this.destroy$)
    ).subscribe((items: any[]) => {
      const notifications = Array.isArray(items) ? items : [];
      this.unreadCount = notifications.filter(item => String(item?.status || '').toLowerCase() === 'unread').length;
      this.recentNotifications = notifications.slice(0, 5);
    });
  }

  toggleNotificationPanel(event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    this.notificationPanelOpen = !this.notificationPanelOpen;
    if (this.notificationPanelOpen) this.loadNotificationPreview();
  }

  closeNotificationPanel(): void {
    this.notificationPanelOpen = false;
  }

  previewIcon(notification: any): string {
    const type = String(notification?.notification_type || notification?.type || '').toUpperCase();
    if (type.includes('PROCUREMENT')) return '📦';
    if (type.includes('ATTENDANCE')) return '✅';
    if (type.includes('DEADLINE')) return '⏰';
    if (type.includes('TASK')) return '📋';
    if (type.includes('PROJECT')) return '📌';
    if (type.includes('MAINTENANCE') || type.includes('RESOURCE')) return '🛠️';
    return '🔔';
  }

  isAdmin(): boolean { return this.role === 'ADMIN'; }
  isProjectManager(): boolean { return this.role === 'PROJECT_MANAGER'; }
  isSiteEngineer(): boolean { return this.role === 'SITE_ENGINEER'; }
  canManageResources(): boolean { return this.isAdmin() || this.isProjectManager(); }
  canManageWorkforceOps(): boolean { return this.isAdmin() || this.isProjectManager() || this.role === 'CONTRACTOR'; }
  canViewDocuments(): boolean { return this.isAdmin() || this.isProjectManager() || this.isSiteEngineer() || this.role === 'CLIENT'; }
  canUseProcurement(): boolean { return this.isAdmin() || this.isProjectManager() || this.role === 'CONTRACTOR'; }
  canViewBudget(): boolean { return this.isAdmin() || this.isProjectManager() || this.isSiteEngineer() || this.role === 'CLIENT'; }
  canViewReports(): boolean { return this.isAdmin() || this.isProjectManager() || this.isSiteEngineer() || this.role === 'CLIENT'; }
  canViewAnalytics(): boolean { return this.isAdmin() || this.isProjectManager(); }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    this.notificationPanelOpen = false;
    this.router.navigate(['/login']);
  }
}
