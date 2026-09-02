import { Routes } from '@angular/router';

import { authGuard, roleGuard } from './guards/auth-guard';

// =====================================================
// AUTHENTICATION
// =====================================================

import { Login } from './pages/auth/login/login';
import { Register } from './pages/auth/register/register';
import { ForgotPassword } from './pages/auth/forgot-password/forgot-password';
import { ResetPassword } from './pages/auth/reset-password/reset-password';

// =====================================================
// DASHBOARDS
// =====================================================

import { AdminDashboard } from './pages/dashboards/admin-dashboard/admin-dashboard';
import { ProjectManagerDashboard } from './pages/dashboards/project-manager-dashboard/project-manager-dashboard';
import { SiteEngineerDashboard } from './pages/dashboards/site-engineer-dashboard/site-engineer-dashboard';
import { ContractorDashboard } from './pages/dashboards/contractor-dashboard/contractor-dashboard';
import { WorkerDashboard } from './pages/dashboards/worker-dashboard/worker-dashboard';
import { ClientDashboard } from './pages/dashboards/client-dashboard/client-dashboard';

// =====================================================
// NOTIFICATIONS
// =====================================================

import { AdminNotifications } from './pages/admin-notifications/admin-notifications';
import { ContractorNotifications } from './pages/contractor-notifications/contractor-notifications';
import { ClientNotifications } from './pages/client-notifications/client-notifications';
import { WorkerNotifications } from './pages/worker-notifications/worker-notifications';
import { SiteEngineerNotifications } from './pages/site-engineer-notifications/site-engineer-notifications';

import { Notifications } from './pages/notifications/notifications';
import { NotificationDetails } from './pages/notifications/notification-details/notification-details';

// =====================================================
// USER MANAGEMENT
// =====================================================

import { UserManagement } from './pages/user-management/user-management';

// =====================================================
// RESOURCES
// =====================================================

import { ResourceAllocation } from './pages/resources/resource-allocation/resource-allocation';

// =====================================================
// PROJECTS
// =====================================================

import { ProjectList } from './pages/projects/project-list/project-list';
import { CreateProject } from './pages/projects/create-project/create-project';
import { Milestones } from './pages/projects/milestones/milestones';
import { ProjectDetails } from './pages/projects/project-details/project-details';
import { ProjectStatus } from './pages/projects/project-status/project-status';
import { Schedule } from './pages/projects/schedule/schedule';
import { UpdateProject } from './pages/projects/update-project/update-project';

// =====================================================
// SITE ENGINEER
// =====================================================

import { SiteEngineerProjects } from './pages/site-engineer-projects/site-engineer-projects';
import { SiteEngineerMilestones } from './pages/site-engineer-milestones/site-engineer-milestones';

// =====================================================
// OTHER MODULES
// =====================================================

import { Profile } from './pages/profile/profile';
import { Inventory } from './pages/inventory/inventory';
import { Workforce } from './pages/workforce/workforce';
import { Attendance } from './pages/attendance/attendance';
import { Reports } from './pages/reports/reports';
import { Analytics } from './pages/analytics/analytics';

// =====================================================
// PROCUREMENT REQUESTS
// =====================================================

import { Requests } from './pages/procurement/requests/requests';

// =====================================================
// ROUTES
// =====================================================

export const routes: Routes = [

  // =====================================================
  // DEFAULT
  // =====================================================

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  // =====================================================
  // AUTHENTICATION
  // =====================================================

  {
    path: 'login',
    component: Login
  },

  {
    path: 'register',
    component: Register
  },

  {
    path: 'forgot-password',
    component: ForgotPassword
  },

  {
    path: 'reset-password',
    component: ResetPassword
  },

  // =====================================================
  // DASHBOARDS
  // =====================================================

  {
    path: 'admin-dashboard',
    component: AdminDashboard,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN'])
    ]
  },

  {
    path: 'project-manager-dashboard',
    component: ProjectManagerDashboard,
    canActivate: [
      authGuard,
      roleGuard(['PROJECT_MANAGER'])
    ]
  },

  {
    path: 'site-engineer-dashboard',
    component: SiteEngineerDashboard,
    canActivate: [
      authGuard,
      roleGuard(['SITE_ENGINEER'])
    ]
  },

  {
    path: 'contractor-dashboard',
    component: ContractorDashboard,
    canActivate: [
      authGuard,
      roleGuard(['CONTRACTOR'])
    ]
  },

  {
    path: 'worker-dashboard',
    component: WorkerDashboard,
    canActivate: [
      authGuard,
      roleGuard(['WORKER'])
    ]
  },

  {
    path: 'client-dashboard',
    component: ClientDashboard,
    canActivate: [
      authGuard,
      roleGuard(['CLIENT'])
    ]
  },

  // =====================================================
  // USER MANAGEMENT
  // =====================================================

  {
    path: 'user-management',
    component: UserManagement,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN'])
    ]
  },

  // =====================================================
  // PROFILE
  // =====================================================

  {
    path: 'profile',
    component: Profile,
    canActivate: [authGuard]
  },

  // =====================================================
  // RESOURCE MANAGEMENT
  // =====================================================

  {
    path: 'resource-allocation',
    component: ResourceAllocation,
    canActivate: [authGuard]
  },

  {
    path: 'resources/resource-allocation',
    component: ResourceAllocation,
    canActivate: [authGuard]
  },

  // =====================================================
  // PROJECT MANAGEMENT
  // =====================================================

  {
    path: 'projects',
    component: ProjectList,
    canActivate: [authGuard]
  },

  {
    path: 'projects/create-project',
    component: CreateProject,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN', 'PROJECT_MANAGER'])
    ]
  },

  {
    path: 'projects/milestones',
    component: Milestones,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN', 'PROJECT_MANAGER'])
    ]
  },

  {
    path: 'projects/project-details/:id',
    component: ProjectDetails,
    canActivate: [authGuard]
  },

  {
    path: 'projects/project-status',
    component: ProjectStatus,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN', 'PROJECT_MANAGER'])
    ]
  },

  {
    path: 'projects/schedule',
    component: Schedule,
    canActivate: [authGuard]
  },

  {
    path: 'projects/update-project/:id',
    component: UpdateProject,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN', 'PROJECT_MANAGER'])
    ]
  },

  // =====================================================
  // SITE ENGINEER
  // =====================================================

  {
    path: 'site-engineer-projects',
    component: SiteEngineerProjects,
    canActivate: [authGuard]
  },

  {
    path: 'site-engineer-milestones',
    component: SiteEngineerMilestones,
    canActivate: [authGuard]
  },

  // =====================================================
  // INVENTORY
  // =====================================================

  {
    path: 'inventory',
    component: Inventory,
    canActivate: [authGuard]
  },

  // =====================================================
  // WORKFORCE
  // =====================================================

  {
    path: 'workforce',
    component: Workforce,
    canActivate: [authGuard]
  },

  // =====================================================
  // ATTENDANCE
  // =====================================================

  {
    path: 'attendance',
    component: Attendance,
    canActivate: [authGuard]
  },

  // =====================================================
  // PROCUREMENT MANAGEMENT
  // =====================================================

  {
    path: 'procurement',
    loadComponent: () =>
      import('./pages/procurement/procurement')
        .then(m => m.Procurement),
    canActivate: [authGuard]
  },

  // =====================================================
  // PROCUREMENT REQUESTS
  // =====================================================

  {
    path: 'procurement/requests',
    component: Requests,
    canActivate: [authGuard]
  },

  // =====================================================
  // VENDOR MANAGEMENT
  // =====================================================

  {
    path: 'procurement/vendors',
    loadComponent: () =>
      import('./pages/procurement/vendors/vendors')
        .then(m => m.Vendors),
    canActivate: [authGuard]
  },

  // =====================================================
  // PURCHASE ORDERS
  // =====================================================

  {
    path: 'procurement/purchase-orders',
    loadComponent: () =>
      import('./pages/procurement/purchase-orders/purchase-orders')
        .then(m => m.PurchaseOrders),
    canActivate: [authGuard]
  },

  // =====================================================
  // INVOICES
  // =====================================================

  {
    path: 'procurement/invoices',
    loadComponent: () =>
      import('./pages/procurement/invoices/invoices')
        .then(m => m.Invoices),
    canActivate: [authGuard]
  },

  // =====================================================
  // CATEGORIES
  // =====================================================

  {
    path: 'procurement/categories',
    loadComponent: () =>
      import('./pages/procurement/categories/categories')
        .then(m => m.Categories),
    canActivate: [authGuard]
  },

  // =====================================================
  // REPORTS
  // =====================================================

  {
    path: 'reports',
    component: Reports,
    canActivate: [authGuard]
  },

  // =====================================================
  // ANALYTICS
  // =====================================================

  {
    path: 'analytics',
    component: Analytics,
    canActivate: [authGuard]
  },

  // =====================================================
  // NOTIFICATIONS
  // =====================================================

  {
    path: 'notifications',
    component: Notifications,
    canActivate: [authGuard]
  },

  // =====================================================
  // NOTIFICATION DETAILS
  // IMPORTANT:
  // This route must come after /notifications
  // and before wildcard route.
  // =====================================================

  {
    path: 'notification-details/:id',
    component: NotificationDetails,
    canActivate: [authGuard]
  },

  // =====================================================
  // ADMIN NOTIFICATIONS
  // =====================================================

  {
    path: 'admin-notifications',
    component: AdminNotifications,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN'])
    ]
  },

  // =====================================================
  // CONTRACTOR NOTIFICATIONS
  // =====================================================

  {
    path: 'contractor-notifications',
    component: ContractorNotifications,
    canActivate: [
      authGuard,
      roleGuard(['CONTRACTOR'])
    ]
  },

  // =====================================================
  // CLIENT NOTIFICATIONS
  // =====================================================

  {
    path: 'client-notifications',
    component: ClientNotifications,
    canActivate: [
      authGuard,
      roleGuard(['CLIENT'])
    ]
  },

  // =====================================================
  // WORKER NOTIFICATIONS
  // =====================================================

  {
    path: 'worker-notifications',
    component: WorkerNotifications,
    canActivate: [
      authGuard,
      roleGuard(['WORKER'])
    ]
  },

  // =====================================================
  // SITE ENGINEER NOTIFICATIONS
  // =====================================================

  {
    path: 'site-engineer-notifications',
    component: SiteEngineerNotifications,
    canActivate: [
      authGuard,
      roleGuard(['SITE_ENGINEER'])
    ]
  },

  // =====================================================
  // REDIRECT / ALIAS ROUTES
  // =====================================================

  {
    path: 'dashboard',
    redirectTo: 'project-manager-dashboard',
    pathMatch: 'full'
  },

  {
    path: 'projects/create',
    redirectTo: 'projects/create-project',
    pathMatch: 'full'
  },

  {
    path: 'projects/status',
    redirectTo: 'projects/project-status',
    pathMatch: 'full'
  },

  {
    path: 'projects/details/:id',
    redirectTo: 'projects/project-details/:id',
    pathMatch: 'full'
  },

  {
    path: 'resources',
    redirectTo: 'resource-allocation',
    pathMatch: 'full'
  },

  {
    path: 'resources/equipment-tracking',
    redirectTo: 'resource-allocation',
    pathMatch: 'full'
  },

  {
    path: 'resources/resource-utilization',
    redirectTo: 'resource-allocation',
    pathMatch: 'full'
  },

  // =====================================================
  // PAGE NOT FOUND
  // =====================================================

  {
    path: '**',
    redirectTo: 'login'
  }

];