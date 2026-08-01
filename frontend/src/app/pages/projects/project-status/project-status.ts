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