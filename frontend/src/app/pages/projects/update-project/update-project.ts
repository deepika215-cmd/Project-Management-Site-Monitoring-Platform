<<<<<<< HEAD
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProjectService } from '../../../services/project';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-update-project', standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './update-project.html', styleUrl: './update-project.css'
})
export class UpdateProject implements OnInit {
  project: any = { id: 0, name: '', code: '', category: '', priority: '', description: '', clientName: '', clientEmail: '', clientPhone: '', location: '', budget: 0, startDate: '', completionDate: '', manager: '', managerId: 0, status: 'Planning', progress: 0 };
  updateReason = '';
  projectId = 0;
  loading = true;
  errorMessage = '';

  constructor(private route: ActivatedRoute, private router: Router, private projectService: ProjectService) {}

  ngOnInit(): void {
    this.projectId = Number(this.route.snapshot.paramMap.get('id'));
    if (!this.projectId) { this.errorMessage = 'Invalid project ID.'; this.loading = false; return; }
    this.projectService.getProjects().subscribe({
      next: projects => {
        const match = (Array.isArray(projects) ? projects : []).find(p => Number(p.id) === this.projectId);
        if (match) {
          this.project = this.projectService.toViewModel(match);
          this.loading = false;
          return;
        }
        this.projectService.getProject(this.projectId).subscribe({
          next: p => { this.project = this.projectService.toViewModel(p); this.loading = false; },
          error: err => { this.errorMessage = err?.error?.detail || 'Unable to load project.'; this.loading = false; }
        });
      },
      error: err => {
        this.projectService.getProject(this.projectId).subscribe({
          next: p => { this.project = this.projectService.toViewModel(p); this.loading = false; },
          error: fallbackErr => { this.errorMessage = fallbackErr?.error?.detail || err?.error?.detail || 'Unable to load project.'; this.loading = false; }
        });
      }
    });
  }

  updateProject(): void {
    this.errorMessage = '';
    if (!this.project.name?.trim() || !this.project.location?.trim() || !this.project.startDate || !this.project.completionDate || this.project.budget === null || !this.project.managerId) {
      this.errorMessage = 'Required project fields are missing.'; return;
    }
    if (Number(this.project.budget) < 0) { this.errorMessage = 'Budget cannot be negative.'; return; }
    if (new Date(this.project.completionDate) < new Date(this.project.startDate)) { this.errorMessage = 'End date cannot be before the start date.'; return; }
    if (this.project.status === 'Closed') { this.errorMessage = 'Closed projects cannot be modified by the backend.'; return; }
    this.loading = true;
    this.projectService.updateProject(this.projectId, {
      project_name: this.project.name,
      description: this.project.description || 'No description provided',
      location: this.project.location,
      start_date: this.project.startDate,
      end_date: this.project.completionDate,
      budget: Number(this.project.budget),
      status: this.project.status,
      manager_id: Number(this.project.managerId)
    }).subscribe({
      next: () => this.router.navigate(['/projects/project-details', this.projectId], { queryParams: { updated: this.projectId } }),
      error: err => { this.loading = false; this.errorMessage = err?.error?.detail || 'Project update failed.'; }
    });
  }
}
=======
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  ActivatedRoute,
  Router,
  RouterLink
} from '@angular/router';

interface Project {

  id: number;

  name: string;

  code: string;

  category: string;

  priority: string;

  description: string;

  clientName: string;

  clientEmail: string;

  clientPhone: string;

  location: string;

  budget: number;

  startDate: string;

  completionDate: string;

  manager: string;

  status: string;

  progress: number;

}


@Component({

  selector: 'app-update-project',

  standalone: true,

  imports: [

    CommonModule,

    FormsModule,

    RouterLink

  ],

  templateUrl: './update-project.html',

  styleUrl: './update-project.css'

})


export class UpdateProject {


  project: Project = {

    id: 1,

    name: 'Green Valley Apartments',

    code: 'BT-001',

    category: 'Residential',

    priority: 'High',

    description:
      'Construction of a modern residential apartment complex with multiple buildings and supporting infrastructure.',

    clientName:
      'Green Valley Developers',

    clientEmail:
      'client@greenvalley.com',

    clientPhone:
      '+91 98765 43210',

    location:
      'Chennai, Tamil Nadu, India',

    budget:
      5000000,

    startDate:
      '2026-01-15',

    completionDate:
      '2027-06-30',

    manager:
      'Raj Kumar',

    status:
      'In Progress',

    progress:
      65

  };


  updateReason = '';


  projectId: string | null = null;


  constructor(

    private route: ActivatedRoute,

    private router: Router

  ) {


    this.projectId =

      this.route.snapshot.paramMap.get('id');


    console.log(

      'Updating Project ID:',

      this.projectId

    );

  }


  updateProject(): void {


    console.log(

      'Updated Project:',

      this.project

    );


    console.log(

      'Update Reason:',

      this.updateReason

    );


    alert(

      'Project updated successfully!'

    );


    this.router.navigate(

      ['/projects/details', this.project.id]

    );

  }

}
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
