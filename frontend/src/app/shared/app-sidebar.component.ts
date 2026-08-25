import { Component, Input, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
@Component({selector:'app-sidebar',standalone:true,imports:[CommonModule,RouterLink],templateUrl:'./app-sidebar.component.html',styleUrl:'./app-sidebar.component.css'})
export class AppSidebarComponent implements OnInit{
 @Input() active=''; role=''; dashboardLink='/project-manager-dashboard'; notificationLink='/notifications';
 constructor(private router:Router){} ngOnInit(){this.syncUser()}
 private syncUser(){try{this.role=String(JSON.parse(localStorage.getItem('currentUser')||'{}')?.role||'').toUpperCase()}catch{this.role=''}
 const d:any={ADMIN:'/admin-dashboard',PROJECT_MANAGER:'/project-manager-dashboard',SITE_ENGINEER:'/site-engineer-dashboard',CONTRACTOR:'/contractor-dashboard',WORKER:'/worker-dashboard',CLIENT:'/client-dashboard'};
 const n:any={ADMIN:'/admin-notifications',PROJECT_MANAGER:'/notifications',SITE_ENGINEER:'/site-engineer-notifications',CONTRACTOR:'/contractor-notifications',WORKER:'/worker-notifications',CLIENT:'/client-notifications'};this.dashboardLink=d[this.role]||'/project-manager-dashboard';this.notificationLink=n[this.role]||'/notifications'}
 isAdmin(){return this.role==='ADMIN'} isProjectManager(){return this.role==='PROJECT_MANAGER'} isSiteEngineer(){return this.role==='SITE_ENGINEER'}
 canManageResources(){return this.isAdmin()||this.isProjectManager()} canUseProcurement(){return this.isAdmin()||this.isProjectManager()||this.role==='CONTRACTOR'} canViewReports(){return this.isAdmin()||this.isProjectManager()||this.isSiteEngineer()} canViewAnalytics(){return this.isAdmin()||this.isProjectManager()}
 logout(){localStorage.removeItem('token');localStorage.removeItem('currentUser');this.router.navigate(['/login'])}
}
