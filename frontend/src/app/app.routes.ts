import { Routes } from '@angular/router';
import { authGuard, roleGuard } from './guards/auth-guard';

import { Login } from './pages/auth/login/login';
import { Register } from './pages/auth/register/register';
import { ForgotPassword } from './pages/auth/forgot-password/forgot-password';
import { ResetPassword } from './pages/auth/reset-password/reset-password';
import { AdminDashboard } from './pages/dashboards/admin-dashboard/admin-dashboard';
import { ContractorDashboard } from './pages/dashboards/contractor-dashboard/contractor-dashboard';
import { WorkerDashboard } from './pages/dashboards/worker-dashboard/worker-dashboard';
import { ClientDashboard } from './pages/dashboards/client-dashboard/client-dashboard';
import { ProjectManagerDashboard } from './pages/dashboards/project-manager-dashboard/project-manager-dashboard';
import { SiteEngineerDashboard } from './pages/dashboards/site-engineer-dashboard/site-engineer-dashboard';

import { AdminNotifications } from './pages/admin-notifications/admin-notifications';
import { ContractorNotifications } from './pages/contractor-notifications/contractor-notifications';
import { ClientNotifications } from './pages/client-notifications/client-notifications';
import { WorkerNotifications } from './pages/worker-notifications/worker-notifications';
import { SiteEngineerNotifications } from './pages/site-engineer-notifications/site-engineer-notifications';

import { UserManagement } from './pages/user-management/user-management';
import { ResourceAllocation } from './pages/resources/resource-allocation/resource-allocation';

import { ProjectList } from './pages/projects/project-list/project-list';
import { CreateProject } from './pages/projects/create-project/create-project';
import { Milestones } from './pages/projects/milestones/milestones';
import { ProjectDetails } from './pages/projects/project-details/project-details';
import { ProjectStatus } from './pages/projects/project-status/project-status';
import { Schedule } from './pages/projects/schedule/schedule';
import { UpdateProject } from './pages/projects/update-project/update-project';

import { SiteEngineerProjects } from './pages/site-engineer-projects/site-engineer-projects';
import { SiteEngineerMilestones } from './pages/site-engineer-milestones/site-engineer-milestones';

import { Notifications } from './pages/notifications/notifications';
import { Profile } from './pages/profile/profile';
import { Inventory } from './pages/inventory/inventory';
import { Workforce } from './pages/workforce/workforce';
import { Attendance } from './pages/attendance/attendance';


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
    canActivate: [authGuard]
  },

  {
    path: 'resources/resource-allocation',
    component: ResourceAllocation,
    canActivate: [authGuard]

  },


  // Projects

  {
    path: 'projects',
    component: ProjectList,
    canActivate: [authGuard]
  },

  {
    path: 'projects/create-project',
    component: CreateProject,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'projects/milestones',
    component: Milestones,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'projects/project-details/:id',
    component: ProjectDetails,
    canActivate: [authGuard]
  },

  {
    path: 'projects/project-status',
    component: ProjectStatus,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },

  {
    path: 'projects/schedule',
    component: Schedule,
    canActivate: [authGuard]
  },

  {
    path: 'projects/update-project/:id',
    component: UpdateProject,
    canActivate: [authGuard, roleGuard(['ADMIN', 'PROJECT_MANAGER'])]
  },


  // Site Engineer

  {
    path: 'site-engineer-projects',
    component: SiteEngineerProjects,
    canActivate: [authGuard, roleGuard(['SITE_ENGINEER'])]
  },

  {
    path: 'site-engineer-milestones',
    component: SiteEngineerMilestones,
    canActivate: [authGuard, roleGuard(['SITE_ENGINEER'])]
  },



  { path: 'inventory', component: Inventory, canActivate: [authGuard] },
  { path: 'workforce', component: Workforce, canActivate: [authGuard] },
  { path: 'attendance', component: Attendance, canActivate: [authGuard] },

  // Notifications

  {
    path: 'notifications',
    component: Notifications,
    canActivate: [authGuard]
  },

  {
    path: 'admin-notifications',
    component: AdminNotifications,
    canActivate: [authGuard]
  },

  {
    path: 'contractor-notifications',
    component: ContractorNotifications,
    canActivate: [authGuard]
  },

  {
    path: 'client-notifications',
    component: ClientNotifications,
    canActivate: [authGuard]
  },

  {
    path: 'worker-notifications',
    component: WorkerNotifications,
    canActivate: [authGuard]
  },

  {
    path: 'site-engineer-notifications',
    component: SiteEngineerNotifications,
    canActivate: [authGuard]
  },


  { path: 'dashboard', redirectTo: 'project-manager-dashboard', pathMatch: 'full' },
  { path: 'projects/create', redirectTo: 'projects/create-project', pathMatch: 'full' },
  { path: 'projects/status', redirectTo: 'projects/project-status', pathMatch: 'full' },
  { path: 'projects/details/:id', redirectTo: 'projects/project-details/:id', pathMatch: 'full' },
  { path: 'resources', redirectTo: 'resource-allocation', pathMatch: 'full' },
  { path: 'resources/equipment-tracking', redirectTo: 'resource-allocation', pathMatch: 'full' },
  { path: 'resources/resource-utilization', redirectTo: 'resource-allocation', pathMatch: 'full' },

];