import { Component, Input, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './app-sidebar.component.html',
  styleUrl: './app-sidebar.component.css'
})
export class AppSidebarComponent implements OnInit {

  @Input() active = '';

  role = '';

  dashboardLink = '/project-manager-dashboard';

  constructor(private router: Router) { }

  ngOnInit(): void {
    this.syncUser();
  }

  private syncUser(): void {

    try {

      const user = JSON.parse(
        localStorage.getItem('currentUser') || '{}'
      );

      this.role = String(
        user?.role || ''
      ).toUpperCase();

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

    this.dashboardLink =
      dashboards[this.role] ||
      '/project-manager-dashboard';
  }


  isAdmin(): boolean {
    return this.role === 'ADMIN';
  }


  isProjectManager(): boolean {
    return this.role === 'PROJECT_MANAGER';
  }


  isSiteEngineer(): boolean {
    return this.role === 'SITE_ENGINEER';
  }


  isContractor(): boolean {
    return this.role === 'CONTRACTOR';
  }


  isWorker(): boolean {
    return this.role === 'WORKER';
  }


  isClient(): boolean {
    return this.role === 'CLIENT';
  }


  logout(): void {

    localStorage.removeItem('token');

    localStorage.removeItem('currentUser');

    this.router.navigate(['/login']);

  }

}