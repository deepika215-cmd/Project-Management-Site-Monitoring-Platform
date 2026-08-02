import { Routes } from '@angular/router';

import { Login } from './pages/auth/login/login';
import { Register } from './pages/auth/register/register';
import { ForgotPassword } from './pages/auth/forgot-password/forgot-password';

import { AdminDashboard } from './pages/dashboards/admin-dashboard/admin-dashboard';
import { ProjectManagerDashboard } from './pages/dashboards/project-manager-dashboard/project-manager-dashboard';
import { SiteEngineerDashboard } from './pages/dashboards/site-engineer-dashboard/site-engineer-dashboard';
import { ContractorDashboard } from './pages/dashboards/contractor-dashboard/contractor-dashboard';
import { WorkerDashboard } from './pages/dashboards/worker-dashboard/worker-dashboard';
import { ClientDashboard } from './pages/dashboards/client-dashboard/client-dashboard';

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
import { Notifications } from './pages/notifications/notifications';

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

  // Dashboards
  {
    path: 'admin-dashboard',
    component: AdminDashboard
  },
  {
    path: 'project-manager-dashboard',
    component: ProjectManagerDashboard
  },
  {
    path: 'site-engineer-dashboard',
    component: SiteEngineerDashboard
  },
  {
    path: 'contractor-dashboard',
    component: ContractorDashboard
  },
  {
    path: 'worker-dashboard',
    component: WorkerDashboard
  },
  {
    path: 'client-dashboard',
    component: ClientDashboard
  },

  // User Management
  {
    path: 'user-management',
    component: UserManagement
  },

  // Project Management
  {
    path: 'projects',
    component: ProjectList
  },
  {
    path: 'projects/create-project',
    component: CreateProject
  },
  {
    path: 'projects/milestones',
    component: Milestones
  },
  {
    path: 'projects/project-details',
    component: ProjectDetails
  },
  {
    path: 'projects/project-status',
    component: ProjectStatus
  },
  {
    path: 'projects/schedule',
    component: Schedule
  },
  {
    path: 'projects/update-project',
    component: UpdateProject
  },
  {
    path: 'site-engineer-projects',
    component: SiteEngineerProjects
  },
  {
    path: 'resource-allocation',
    component: ResourceAllocation
  },
  {
    path: 'resources/resource-allocation',
    component: ResourceAllocation
  },
  {
    path: 'notifications',
    component: Notifications
  },

  // Optional pages (add these after creating the components)
  /*
  {
    path: 'profile',
    component: ProfileComponent
  }
  */

];