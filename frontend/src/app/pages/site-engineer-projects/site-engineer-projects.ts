import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ProjectService, Project } from '../../services/project';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';
@Component({selector:'app-site-engineer-projects',standalone:true,imports:[CommonModule,RouterLink,AppSidebarComponent],templateUrl:'./site-engineer-projects.html',styleUrl:'./site-engineer-projects.css'})
export class SiteEngineerProjects implements OnInit{
  projects:Project[]=[];loading=false;error='';
  constructor(private projectService:ProjectService){}
  getCount(status:string){return this.projects.filter(p=>p.status===status).length;}
  ngOnInit(){this.loading=true;this.projectService.getProjects().subscribe({next:data=>{this.projects=data.map(p=>this.projectService.toViewModel(p));this.loading=false},error:e=>{this.loading=false;this.error=e?.error?.detail||'Unable to load projects.'}})}
}
