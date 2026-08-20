import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-resource-utilization',
  imports: [CommonModule, FormsModule],
  templateUrl: './resource-utilization.html',
  styleUrl: './resource-utilization.css',
})
export class ResourceUtilization {
  period = 'This Week';
  resources = [
    { name: 'CAT 320 Excavator', category: 'Excavators', planned: 50, actual: 46, utilization: 92, project: 'Residential Complex' },
    { name: 'ACE 14XW Crane', category: 'Cranes', planned: 50, actual: 44, utilization: 88, project: 'Bridge Construction' },
    { name: 'Transit Mixer 6m³', category: 'Concrete Mixers', planned: 50, actual: 43, utilization: 85, project: 'Highway Project' },
    { name: 'Tata 2518', category: 'Dump Trucks', planned: 50, actual: 39, utilization: 78, project: 'Residential Complex' },
    { name: 'Diesel Generator 125kVA', category: 'Generators', planned: 50, actual: 38, utilization: 75, project: 'Mall Construction' },
  ];
  get average() { return Math.round(this.resources.reduce((sum, r) => sum + r.utilization, 0) / this.resources.length); }
}
