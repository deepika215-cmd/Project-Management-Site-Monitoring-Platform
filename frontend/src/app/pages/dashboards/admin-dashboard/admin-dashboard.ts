import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import Swal from 'sweetalert2';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css'
})
export class AdminDashboard implements OnInit {
  loading = true;
  error = '';
  summary = { projects: 0, activeProjects: 0, completedProjects: 0, users: 0, workers: 0, procurements: 0, inventory: 0, notifications: 0 };
  recentProjects: any[] = [];
  recentProcurements: any[] = [];

  constructor(private router: Router, private api: Api) {}

  ngOnInit(): void { this.loadDashboard(); }

  loadDashboard(): void {
    this.loading = true;
    this.error = '';
    forkJoin({
      analytics: this.api.getAnalytics(),
      users: this.api.getUsers(),
      projects: this.api.getProjects(),
      procurements: this.api.getProcurements(),
      notifications: this.api.getNotifications()
    }).subscribe({
      next: ({ analytics, users, projects, procurements, notifications }) => {
        const a = analytics || {};
        this.summary = {
          projects: Number(a?.projects?.total ?? 0),
          activeProjects: Number(a?.projects?.active ?? 0),
          completedProjects: Number(a?.projects?.completed ?? 0),
          users: Array.isArray(users) ? users.length : 0,
          workers: Number(a?.workers?.total ?? 0),
          procurements: Number(a?.procurements?.total ?? 0),
          inventory: Number(a?.inventory?.total ?? 0),
          notifications: Array.isArray(notifications) ? notifications.length : 0
        };
        this.recentProjects = (Array.isArray(projects) ? projects : []).slice(-5).reverse();
        this.recentProcurements = (Array.isArray(procurements) ? procurements : []).slice(-5).reverse();
        this.loading = false;
      },
      error: err => {
        this.loading = false;
        this.error = err?.error?.detail || 'Unable to load administrator data from the backend.';
      }
    });
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    Swal.fire({ icon: 'success', title: 'Logged Out', text: 'You have been logged out successfully.', confirmButtonColor: '#2563eb' })
      .then(() => this.router.navigate(['/login']));
  }
}
