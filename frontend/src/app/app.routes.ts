import { Routes } from '@angular/router';
import { LoginComponent } from './modules/auth/login/login.component';
import { RegisterComponent } from './modules/auth/register/register.component';
import { DashboardComponent } from './modules/dashboard/dashboard/dashboard.component';
import { ProjectManagerDashboardComponent } from './modules/project/project-manager-dashboard/project-manager-dashboard.component';
import { SiteEngineerDashboardComponent } from './modules/site/site-engineer-dashboard/site-engineer-dashboard.component';
import { ContractorDashboardComponent } from './modules/contractor/contractor-dashboard/contractor-dashboard.component';
import { ClientDashboardComponent } from './modules/client/client-dashboard/client-dashboard.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'project-manager', component: ProjectManagerDashboardComponent },
  { path: 'site-engineer', component: SiteEngineerDashboardComponent },
  { path: 'contractor', component: ContractorDashboardComponent },
  { path: 'client', component: ClientDashboardComponent }
];
