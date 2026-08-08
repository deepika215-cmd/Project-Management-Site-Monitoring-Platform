import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-contractor-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './contractor-dashboard.html',
  styleUrl: './contractor-dashboard.css'
})
export class ContractorDashboard {

  contracts = [
    {
      project: 'Green Valley Apartments',
      work: 'Foundation Work',
      status: 'In Progress'
    },
    {
      project: 'City Mall Construction',
      work: 'Electrical Installation',
      status: 'Pending'
    },
    {
      project: 'Industrial Warehouse',
      work: 'Roofing',
      status: 'Completed'
    }
  ];

}