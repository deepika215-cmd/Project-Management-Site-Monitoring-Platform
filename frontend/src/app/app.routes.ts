import { Routes } from '@angular/router';
import { authGuard, roleGuard, dashboardGuard } from './guards/auth-guard';

import { Login } from './pages/auth/login/login';
import { Register } from './pages/auth/register/register';
import { ForgotPassword } from './pages/auth/forgot-password/forgot-password';
import { ResetPassword } from './pages/auth/reset-password/reset-password';

import { AdminDashboard } from './pages/dashboards/admin-dashboard/admin-dashboard';
import { ProjectManagerDashboard } from './pages/dashboards/project-manager-dashboard/project-manager-dashboard';
import { SiteEngineerDashboard } from './pages/dashboards/site-engineer-dashboard/site-engineer-dashboard';
import { ContractorDashboard } from './pages/dashboards/contractor-dashboard/contractor-dashboard';
import { WorkerDashboard } from './pages/dashboards/worker-dashboard/worker-dashboard';
import { ClientDashboard } from './pages/dashboards/client-dashboard/client-dashboard';

import { AdminNotifications } from './pages/admin-notifications/admin-notifications';
import { ContractorNotifications } from './pages/contractor-notifications/contractor-notifications';
import { ClientNotifications } from './pages/client-notifications/client-notifications';
import { WorkerNotifications } from './pages/worker-notifications/worker-notifications';
import { SiteEngineerNotifications } from './pages/site-engineer-notifications/site-engineer-notifications';

import { UserManagement } from './pages/user-management/user-management';
import { ResourceAllocation } from './pages/resources/resource-allocation/resource-allocation';

import { ProjectList } from './pages/projects/project-list/project-list';
import { CreateProject } from './pages/projects/create-project/create-project';
import { ProjectManagerCreateProject } from './pages/project-manager-create-project/project-manager-create-project';
import { SiteEngineerCreateProject } from './pages/site-engineer-create-project/site-engineer-create-project';
import { Milestones } from './pages/projects/milestones/milestones';
import { ProjectDetails } from './pages/projects/project-details/project-details';
import { ProjectStatus } from './pages/projects/project-status/project-status';
import { Schedule } from './pages/projects/schedule/schedule';
import { UpdateProject } from './pages/projects/update-project/update-project';

import { SiteEngineerMilestones } from './pages/site-engineer-milestones/site-engineer-milestones';

import { Notifications } from './pages/notifications/notifications';
import { Profile } from './pages/profile/profile';
import { Inventory } from './pages/inventory/inventory';
import { Workforce } from './pages/workforce/workforce';
import { Attendance } from './pages/attendance/attendance';
import { Procurement } from './pages/procurement/procurement';
import { Reports } from './pages/reports/reports';
import { Analytics } from './pages/analytics/analytics';
import { ProjectOverview } from './pages/project-overview/project-overview';
import { SiteProgress } from './pages/site-progress/site-progress';
import { ResourceOperations } from './pages/resources/resource-operations/resource-operations';
import { WorkforceOperations } from './pages/workforce/workforce-operations/workforce-operations';
import { Documents } from './pages/documents/documents';
import { Budget } from './pages/budget/budget';
import { NotFound } from './pages/not-found/not-found';


export const routes: Routes = [

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },

  // Authentication

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


  // Dashboards

  {
    path: 'admin-dashboard',
    component: AdminDashboard,
    canActivate: [authGuard, roleGuard(['ADMIN'])]
  },

  {
    path: 'project-manager-dashboard',
    component: ProjectManagerDashboard,
    canActivate: [authGuard, roleGuard(['PROJECT_MANAGER'])]
  },

  {
    path: 'site-engineer-dashboard',
    component: SiteEngineerDashboard,
    canActivate: [authGuard, roleGuard(['SITE_ENGINEER'])]
  },

  {
    path: 'contractor-dashboard',
    component: ContractorDashboard,
    canActivate: [authGuard, roleGuard(['CONTRACTOR'])]
  },

  {
    path: 'worker-dashboard',
    component: WorkerDashboard,
    canActivate: [authGuard, roleGuard(['WORKER'])]
  },

  {
    path: 'client-dashboard',
    component: ClientDashboard,
    canActivate: [authGuard, roleGuard(['CLIENT'])]
  },


  // User Management

  {
    path: 'user-management',
    component: UserManagement,
    canActivate: [authGuard, roleGuard(['ADMIN'])]
  },


  // Profile

  {
    path: 'profile',
    component: Profile,
    canActivate: [authGuard]
  },


  // Resources

  {
    path: 'resource-allocation',
    component: ResourceAllocation,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])
    ]
  },

  {
    path: 'resources/resource-allocation',
    component: ResourceAllocation,
    canActivate: [
      authGuard,
      roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])
    ]
  },


  // Projects

  {
    path: 'projects',
    component: ProjectList,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CONTRACTOR', 'CLIENT'])]
  },

  {
    path: 'projects/create-project',
    component: CreateProject,
    canActivate: [authGuard, roleGuard(['ADMIN'])]
  },

  {
    path: 'project-manager/create-project',
    component: ProjectManagerCreateProject,
    canActivate: [authGuard, roleGuard(['PROJECT_MANAGER'])]
  },

  {
    path: 'site-engineer/create-project',
    component: SiteEngineerCreateProject,
    canActivate: [authGuard, roleGuard(['SITE_ENGINEER'])]
  },

  {
    path: 'projects/milestones',
    component: Milestones,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'projects/project-details/:id',
    component: ProjectDetails,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CONTRACTOR', 'CLIENT'])]
  },

  {
    path: 'projects/project-status',
    component: ProjectStatus,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'projects/schedule',
    component: Schedule,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])]
  },

  {
    path: 'projects/update-project/:id',
    component: UpdateProject,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'projects/edit/:id',
    component: UpdateProject,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'admin/projects/update-project/:id',
    component: UpdateProject,
    canActivate: [authGuard, roleGuard(['ADMIN'])]
  },

  {
    path: 'project-manager/update-project/:id',
    component: UpdateProject,
    canActivate: [authGuard, roleGuard(['PROJECT_MANAGER'])]
  },


  // Site Progress Monitoring (Module 3)
  { path: 'site-progress', component: SiteProgress, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CONTRACTOR'])] },
  { path: 'site-progress/daily', redirectTo: 'site-progress', pathMatch: 'full' },
  { path: 'site-progress/weekly', redirectTo: 'site-progress', pathMatch: 'full' },
  { path: 'site-progress/delays', redirectTo: 'site-progress', pathMatch: 'full' },

  // Resource Operations (Module 4)
  { path: 'resources/operations', component: ResourceOperations, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])] },
  { path: 'resources/equipment-tracking', component: ResourceOperations, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])] },
  { path: 'resources/resource-utilization', component: ResourceOperations, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])] },
  { path: 'resources/maintenance', component: ResourceOperations, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])] },

  // Site Engineer

  {
    path: 'site-engineer-projects',
    redirectTo: 'projects',
    pathMatch: 'full'
  },

  { path: 'site-engineer-milestones', redirectTo: 'site-progress', pathMatch: 'full' },



  { path: 'inventory', component: Inventory, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])] },
  { path: 'workforce', component: Workforce, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'CONTRACTOR'])] },
  { path: 'workforce/operations', component: WorkforceOperations, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'CONTRACTOR'])] },
  { path: 'attendance', component: Attendance, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'CONTRACTOR', 'WORKER'])] },

  { path: 'procurement', component: Procurement, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER'])] },
  { path: 'budget', component: Budget, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CLIENT'])] },
  { path: 'reports', component: Reports, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CLIENT'])] },
  { path: 'analytics', component: Analytics, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])] },
  { path: 'project-overview', component: ProjectOverview, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])] },
  { path: 'documents', component: Documents, canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER', 'SITE_ENGINEER', 'CLIENT'])] },

  // Notifications

  {
    path: 'notifications',
    component: Notifications,
    canActivate: [authGuard]
  },

  { path: 'admin-notifications', redirectTo: 'notifications', pathMatch: 'full' },

  { path: 'contractor-notifications', redirectTo: 'notifications', pathMatch: 'full' },

  { path: 'client-notifications', redirectTo: 'notifications', pathMatch: 'full' },

  { path: 'worker-notifications', redirectTo: 'notifications', pathMatch: 'full' },

  { path: 'site-engineer-notifications', redirectTo: 'notifications', pathMatch: 'full' },


  { path: 'dashboard', canActivate: [authGuard, dashboardGuard], component: Profile },
  { path: 'projects/create', redirectTo: 'projects/create-project', pathMatch: 'full' },
  { path: 'projects/status', redirectTo: 'projects/project-status', pathMatch: 'full' },
  { path: 'projects/details/:id', redirectTo: 'projects/project-details/:id', pathMatch: 'full' },
  { path: 'resources', redirectTo: 'resource-allocation', pathMatch: 'full' },

  // Friendly fallback for invalid/dead links. Must remain the final route.
  { path: '**', component: NotFound },

];