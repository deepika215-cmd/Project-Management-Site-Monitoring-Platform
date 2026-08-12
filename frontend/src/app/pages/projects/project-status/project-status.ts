<<<<<<< HEAD
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

interface BackendProject { id: number; project_name: string; description: string; location: string; start_date: string; end_date: string; budget: number; status: string; manager_id: number; }

@Component({
  selector: 'app-project-status',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './project-status.html',
  styleUrl: './project-status.css'
})
export class ProjectStatus implements OnInit {
  projects: BackendProject[] = [];
  selectedProjectId = 0;
  selectedProject: BackendProject | null = null;
  newStatus = '';
  tracking: any = null;
  loading = false;
  loadingProjects = false;
  loadingTracking = false;
  errorMessage = '';

  constructor(private api: Api, private route: ActivatedRoute, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      const requestedId = Number(params.get('projectId') || 0);
      this.loadProjects(requestedId);
    });
  }

  loadProjects(preferredId = this.selectedProjectId): void {
    this.loadingProjects = true;
    this.errorMessage = '';
    this.api.getProjects().subscribe({
      next: (projects: BackendProject[]) => {
        this.projects = Array.isArray(projects) ? projects : [];
        const preferredExists = this.projects.some(p => Number(p.id) === Number(preferredId));
        this.selectedProjectId = preferredExists ? Number(preferredId) : 0;
        this.loadingProjects = false;
        this.selectProject();
        this.cdr.detectChanges();
      },
      error: err => {
        this.loadingProjects = false;
        this.projects = [];
        this.selectedProject = null;
        this.tracking = null;
        this.errorMessage = this.getError(err, 'Unable to load projects. Check that the FastAPI backend is running.');
        this.cdr.detectChanges();
      }
    });
  }

  selectProject(): void {
    this.selectedProjectId = Number(this.selectedProjectId);
    this.selectedProject = this.projects.find(p => Number(p.id) === this.selectedProjectId) || null;
    this.newStatus = this.nextStatuses[0] || '';
    this.tracking = null;
    this.errorMessage = '';
    if (!this.selectedProject) return;

    this.loadTracking(this.selectedProject.id);
  }

  get nextStatuses(): string[] {
    if (!this.selectedProject) return [];
    const transitions: Record<string, string[]> = {
      Planning: ['In Progress'],
      'In Progress': ['Completed'],
      Completed: ['Closed'],
      Closed: []
    };
    return transitions[this.selectedProject.status] || [];
  }

  updateStatus(): void {
    if (!this.selectedProject || !this.newStatus || !this.nextStatuses.includes(this.newStatus)) return;
    this.loading = true;
    this.errorMessage = '';
    this.api.updateProjectStatus(this.selectedProject.id, { status: this.newStatus }).subscribe({
      next: project => {
        this.loading = false;
        const index = this.projects.findIndex(p => Number(p.id) === Number(project.id));
        if (index >= 0) this.projects[index] = project;
        this.selectedProject = project;
        this.newStatus = this.nextStatuses[0] || '';
        this.loadTracking(project.id);
        this.cdr.detectChanges();
      },
      error: err => {
        this.loading = false;
        this.errorMessage = this.getError(err, 'Status update failed. The backend only allows valid lifecycle transitions.');
        this.cdr.detectChanges();
      }
    });
  }

  closeProject(): void {
    if (!this.selectedProject || this.selectedProject.status !== 'Completed') return;
    this.loading = true;
    this.errorMessage = '';
    this.api.closeProject(this.selectedProject.id).subscribe({
      next: project => {
        this.loading = false;
        const index = this.projects.findIndex(p => Number(p.id) === Number(project.id));
        if (index >= 0) this.projects[index] = project;
        this.selectedProject = project;
        this.newStatus = '';
        this.loadTracking(project.id);
        this.cdr.detectChanges();
      },
      error: err => {
        this.loading = false;
        this.errorMessage = this.getError(err, 'Project could not be closed.');
        this.cdr.detectChanges();
      }
    });
  }

  refreshTracking(): void {
    if (!this.selectedProject) return;
    this.loadTracking(this.selectedProject.id);
  }

  private loadTracking(id: number): void {
    this.loadingTracking = true;
    this.tracking = null;
    this.api.getProjectTracking(id).subscribe({
      next: tracking => { this.tracking = tracking; this.loadingTracking = false; this.cdr.detectChanges(); },
      error: err => { this.loadingTracking = false; this.errorMessage = this.getError(err, 'Unable to load project tracking.'); this.cdr.detectChanges(); }
    });
  }

  get completion(): number { return Math.max(0, Math.min(100, Number(this.tracking?.progress ?? 0))); }
  getStatusClass(status: string): string { return ({ Planning:'planning', 'In Progress':'in-progress', Completed:'completed', Closed:'closed' } as Record<string,string>)[status] || ''; }

  private getError(err: any, fallback: string): string {
    const detail = err?.error?.detail;
    if (Array.isArray(detail)) return detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
    return detail || fallback;
  }
}
=======
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';


interface Project {

  id: number;

  code: string;

  name: string;

  manager: string;

  status: string;

  completion: number;

  milestonesCompleted: boolean;

  inspectionApproved: boolean;

  financialSettlement: boolean;

  issuesResolved: boolean;

  clientAccepted: boolean;

}


interface StatusHistory {

  date: string;

  previousStatus: string;

  newStatus: string;

  updatedBy: string;

  reason: string;

}


@Component({

  selector: 'app-project-status',

  standalone: true,

  imports: [

    CommonModule,

    FormsModule,

    RouterLink

  ],

  templateUrl: './project-status.html',

  styleUrl: './project-status.css'

})


export class ProjectStatus {


  selectedProjectId = 1;


  newStatus = 'Planning';


  holdReason = '';


  projects: Project[] = [

    {

      id: 1,

      code: 'BT-001',

      name: 'Green Valley Apartments',

      manager: 'Rajesh Kumar',

      status: 'In Progress',

      completion: 45,

      milestonesCompleted: false,

      inspectionApproved: false,

      financialSettlement: false,

      issuesResolved: true,

      clientAccepted: false

    },


    {

      id: 2,

      code: 'BT-002',

      name: 'City Mall Construction',

      manager: 'Arun Kumar',

      status: 'Planning',

      completion: 10,

      milestonesCompleted: false,

      inspectionApproved: false,

      financialSettlement: false,

      issuesResolved: true,

      clientAccepted: false

    },


    {

      id: 3,

      code: 'BT-003',

      name: 'National Highway Project',

      manager: 'Vijay Raj',

      status: 'Completed',

      completion: 100,

      milestonesCompleted: true,

      inspectionApproved: true,

      financialSettlement: true,

      issuesResolved: true,

      clientAccepted: true

    }

  ];


  selectedProject: Project =

    this.projects[0];


  statusHistory: StatusHistory[] = [

    {

      date: '2026-01-10',

      previousStatus: 'Planning',

      newStatus: 'In Progress',

      updatedBy: 'Rajesh Kumar',

      reason: 'Construction work started.'

    },

    {

      date: '2026-01-05',

      previousStatus: 'Planning',

      newStatus: 'Planning',

      updatedBy: 'Admin',

      reason: 'Project created and assigned to Project Manager.'

    }

  ];


  selectProject(): void {


    const project =

      this.projects.find(

        p =>

          p.id ===

          Number(

            this.selectedProjectId

          )

      );


    if (project) {


      this.selectedProject =

        project;


      this.newStatus =

        project.status;


      this.holdReason = '';

    }

  }


  updateStatus(): void {


    if (

      this.newStatus ===

      this.selectedProject.status

    ) {

      alert(

        'The project is already in this status.'

      );

      return;

    }


    if (

      this.newStatus ===

      'On Hold' &&

      !this.holdReason.trim()

    ) {

      alert(

        'Please provide a reason for putting the project on hold.'

      );

      return;

    }


    const previousStatus =

      this.selectedProject.status;


    let reason =

      'Project status updated.';


    if (

      this.newStatus ===

      'On Hold'

    ) {

      reason =

        this.holdReason;

    }


    this.selectedProject.status =

      this.newStatus;


    this.statusHistory.unshift({

      date:

        new Date()

          .toISOString()

          .split('T')[0],

      previousStatus:

        previousStatus,

      newStatus:

        this.newStatus,

      updatedBy:

        'Current User',

      reason:

        reason

    });


    alert(

      'Project status updated successfully!'

    );


    this.holdReason = '';

  }


  canCloseProject(): boolean {


    return (

      this.selectedProject.milestonesCompleted &&

      this.selectedProject.inspectionApproved &&

      this.selectedProject.financialSettlement &&

      this.selectedProject.issuesResolved &&

      this.selectedProject.clientAccepted

    );

  }


  closeProject(): void {


    if (

      !this.canCloseProject()

    ) {

      alert(

        'The project cannot be closed. Please complete all closure requirements.'

      );

      return;

    }


    const confirmed =

      confirm(

        'Are you sure you want to close this project? Once closed, no further construction activities can be recorded.'

      );


    if (!confirmed) {

      return;

    }


    const previousStatus =

      this.selectedProject.status;


    this.selectedProject.status =

      'Closed';


    this.newStatus =

      'Closed';


    this.statusHistory.unshift({

      date:

        new Date()

          .toISOString()

          .split('T')[0],

      previousStatus:

        previousStatus,

      newStatus:

        'Closed',

      updatedBy:

        'Current User',

      reason:

        'All project closure requirements completed.'

    });


    alert(

      'Project has been successfully closed.'

    );

  }


  getStatusClass(

    status: string

  ): string {


    switch (status) {


      case 'Planning':

        return 'planning';


      case 'In Progress':

        return 'in-progress';


      case 'On Hold':

        return 'on-hold';


      case 'Completed':

        return 'completed';


      case 'Closed':

        return 'closed';


      default:

        return '';

    }

  }

}
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
