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