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
import { ResourceDashboard } from './pages/resources/resource-dashboard/resource-dashboard';
import { MachineryTracking } from './pages/resources/machinery-tracking/machinery-tracking';
import { ResourceUtilization } from './pages/resources/resource-utilization/resource-utilization';
import { ResourceAvailability } from './pages/resources/resource-availability/resource-availability';
import { MaintenanceScheduling } from './pages/resources/maintenance-scheduling/maintenance-scheduling';

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
import { MaterialDashboard } from './pages/materials/material-dashboard/material-dashboard';
import { MaterialProcurement } from './pages/materials/material-procurement/material-procurement';
import { InventoryMonitoring } from './pages/materials/inventory-monitoring/inventory-monitoring';
import { MaterialRequests } from './pages/materials/material-requests/material-requests';
import { MaterialAllocation } from './pages/materials/material-allocation/material-allocation';
import { StockManagement } from './pages/materials/stock-management/stock-management';
import { WorkforceDashboard } from './pages/workforce/workforce-dashboard/workforce-dashboard';
import { WorkerRegistration } from './pages/workforce/worker-registration/worker-registration';
import { AttendanceTracking } from './pages/workforce/attendance-tracking/attendance-tracking';
import { WorkforceAllocation } from './pages/workforce/workforce-allocation/workforce-allocation';
import { ShiftScheduling } from './pages/workforce/shift-scheduling/shift-scheduling';
import { PayrollMonitoring } from './pages/workforce/payroll-monitoring/payroll-monitoring';
import { ProcurementDashboard } from './pages/procurement/procurement-dashboard/procurement-dashboard';
import { VendorManagement } from './pages/procurement/vendor-management/vendor-management';
import { PurchaseOrders } from './pages/procurement/purchase-orders/purchase-orders';
import { InvoiceTracking } from './pages/procurement/invoice-tracking/invoice-tracking';
import { ProcurementRequests } from './pages/procurement/procurement-requests/procurement-requests';
import { SupplierManagement } from './pages/procurement/supplier-management/supplier-management';


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
  {
    path: 'resources/resource-dashboard',
    component: ResourceDashboard,
    canActivate: [authGuard]
  },
  { path: 'resources/machinery-tracking', component: MachineryTracking, canActivate: [authGuard] },
  { path: 'resources/resource-utilization', component: ResourceUtilization, canActivate: [authGuard] },
  { path: 'resources/resource-availability', component: ResourceAvailability, canActivate: [authGuard] },
  { path: 'resources/maintenance-scheduling', component: MaintenanceScheduling, canActivate: [authGuard] },


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
  { path: 'materials/material-dashboard', component: MaterialDashboard, canActivate: [authGuard] },
  { path: 'materials/material-procurement', component: MaterialProcurement, canActivate: [authGuard] },
  { path: 'materials/inventory-monitoring', component: InventoryMonitoring, canActivate: [authGuard] },
  { path: 'materials/material-requests', component: MaterialRequests, canActivate: [authGuard] },
  { path: 'materials/material-allocation', component: MaterialAllocation, canActivate: [authGuard] },
  { path: 'materials/stock-management', component: StockManagement, canActivate: [authGuard] },
  { path: 'workforce/workforce-dashboard', component: WorkforceDashboard, canActivate: [authGuard] },
  { path: 'workforce/worker-registration', component: WorkerRegistration, canActivate: [authGuard] },
  { path: 'workforce/attendance-tracking', component: AttendanceTracking, canActivate: [authGuard] },
  { path: 'workforce/workforce-allocation', component: WorkforceAllocation, canActivate: [authGuard] },
  { path: 'workforce/shift-scheduling', component: ShiftScheduling, canActivate: [authGuard] },
  { path: 'workforce/payroll-monitoring', component: PayrollMonitoring, canActivate: [authGuard] },
  { path: 'procurement/procurement-dashboard', component: ProcurementDashboard, canActivate: [authGuard] },
  { path: 'procurement/vendor-management', component: VendorManagement, canActivate: [authGuard] },
  { path: 'procurement/purchase-orders', component: PurchaseOrders, canActivate: [authGuard] },
  { path: 'procurement/invoice-tracking', component: InvoiceTracking, canActivate: [authGuard] },
  { path: 'procurement/procurement-requests', component: ProcurementRequests, canActivate: [authGuard] },
  { path: 'procurement/supplier-management', component: SupplierManagement, canActivate: [authGuard] },

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
  { path: 'resources', redirectTo: 'resources/resource-dashboard', pathMatch: 'full' },
  { path: 'resources/equipment-tracking', redirectTo: 'resources/machinery-tracking', pathMatch: 'full' },

];
