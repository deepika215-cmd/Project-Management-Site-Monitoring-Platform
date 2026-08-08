import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-worker-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './worker-dashboard.html',
  styleUrl: './worker-dashboard.css'
})
export class WorkerDashboard {

  tasks = [

    {
      project: 'Green Valley Apartments',
      task: 'Foundation Excavation',
      status: 'In Progress'
    },

    {
      project: 'City Mall Construction',
      task: 'Concrete Mixing',
      status: 'Pending'
    },

    {
      project: 'Industrial Warehouse',
      task: 'Brick Wall Construction',
      status: 'Completed'
    }

  ];

}