import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-resource-availability',
  imports: [CommonModule, FormsModule],
  templateUrl: './resource-availability.html',
  styleUrl: './resource-availability.css',
})
export class ResourceAvailability {
  search = '';
  resources = [
    { name: 'JCB 3DX (JCB002)', category: 'Excavators', location: 'Site A', status: 'Available', available: 'Now', next: '—' },
    { name: 'Transit Mixer 6m³ (TMX01)', category: 'Concrete Mixers', location: 'Site B', status: 'Available', available: 'Now', next: '18 Aug 2026' },
    { name: 'Diesel Generator 82kVA (DG03)', category: 'Generators', location: 'Site C', status: 'Available', available: 'Now', next: '—' },
    { name: 'Dump Truck (DT12)', category: 'Dump Trucks', location: 'Site A', status: 'In Use', available: '20 Aug 2026', next: '—' },
    { name: 'Safety Harness Set (SH08)', category: 'Safety Equipment', location: 'Site B', status: 'Reserved', available: '16 Aug 2026', next: '—' },
    { name: 'ACE 14XW Crane', category: 'Cranes', location: 'Site B', status: 'Maintenance', available: '17 Aug 2026', next: 'Hydraulic check' },
  ];
  get filteredResources() { const term = this.search.toLowerCase(); return this.resources.filter(r => r.name.toLowerCase().includes(term) || r.category.toLowerCase().includes(term) || r.location.toLowerCase().includes(term)); }
}
