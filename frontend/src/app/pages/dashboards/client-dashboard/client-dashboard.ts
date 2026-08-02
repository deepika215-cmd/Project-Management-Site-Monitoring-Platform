import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-client-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './client-dashboard.html',
  styleUrl: './client-dashboard.css'
})
export class ClientDashboard {

  projects = [

    {
      name: 'Green Valley Apartments',
      status: 'In Progress',
      progress: 65
    },

    {
      name: 'City Mall Construction',
      status: 'Planning',
      progress: 40
    },

    {
      name: 'Industrial Warehouse',
      status: 'Completed',
      progress: 100
    }

  ];

}