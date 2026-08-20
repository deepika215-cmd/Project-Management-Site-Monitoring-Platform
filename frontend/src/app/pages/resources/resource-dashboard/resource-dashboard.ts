import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-resource-dashboard',
  imports: [CommonModule],
  templateUrl: './resource-dashboard.html',
  styleUrl: './resource-dashboard.css',
})
export class ResourceDashboard {
  readonly stats = [
    { label: 'Total Resources', value: '128', note: '↑ 8 this week', icon: '🚜', tone: 'blue' },
    { label: 'In Use', value: '86', note: '67.2% of total', icon: '🚚', tone: 'green' },
    { label: 'Available', value: '28', note: '21.9% of total', icon: '✓', tone: 'purple' },
    { label: 'Under Maintenance', value: '10', note: '7.8% of total', icon: '🔧', tone: 'orange' },
    { label: 'Out of Service', value: '4', note: '3.1% of total', icon: '⊘', tone: 'red' },
  ];

  readonly categories = [
    { name: 'Excavators', count: 30, color: '#1769e8', icon: '🚜' },
    { name: 'Concrete Mixers', count: 26, color: '#13a879', icon: '🚚' },
    { name: 'Cranes', count: 23, color: '#f39200', icon: '🏗️' },
    { name: 'Dump Trucks', count: 19, color: '#7a43c6', icon: '🚛' },
    { name: 'Generators', count: 16, color: '#08a0bd', icon: '⚡' },
    { name: 'Safety Equipment', count: 14, color: '#008c61', icon: '⛑' },
  ];

  readonly allocationRows = [
    ['RA-2026-101', 'CAT 320 Excavator', 'Excavators', 'Residential Complex', 'Raj Equipment Co.', '09 Aug 2026', '20 Aug 2026', 'Active'],
    ['RA-2026-102', 'JCB 3DX', 'Excavators', 'Mall Construction', 'Suresh Infra', '08 Aug 2026', '18 Aug 2026', 'Active'],
    ['RA-2026-103', 'Transit Mixer 6m³', 'Concrete Mixers', 'Highway Project', 'Mixwell Pvt. Ltd.', '07 Aug 2026', '25 Aug 2026', 'Active'],
    ['RA-2026-104', 'ACE 14XW Crane', 'Cranes', 'Bridge Construction', 'Krane Services', '09 Aug 2026', '30 Aug 2026', 'Active'],
    ['RA-2026-105', 'Tata 2518', 'Dump Trucks', 'Residential Complex', 'Mahadev Transport', '08 Aug 2026', '20 Aug 2026', 'Pending'],
  ];

  readonly maintenanceRows = [
    ['MT-2026-201', 'CAT 320 Excavator', 'Engine Service', '12 Aug 2026', 'Upcoming'],
    ['MT-2026-202', 'Transit Mixer 6m³', 'Drum Inspection', '13 Aug 2026', 'Upcoming'],
    ['MT-2026-203', 'ACE 14XW Crane', 'Hydraulic Check', '14 Aug 2026', 'Upcoming'],
    ['MT-2026-204', 'Diesel Generator 125kVA', 'General Service', '15 Aug 2026', 'Due Soon'],
    ['MT-2026-205', 'Tata 2518', 'Brake Service', '16 Aug 2026', 'Due Soon'],
  ];

  readonly availabilityRows = [
    ['JCB 3DX (JCB002)', 'Excavators', 'Site A', 'Available', 'Now'],
    ['Transit Mixer 6m³ (TMX01)', 'Concrete Mixers', 'Site B', 'Available', 'Now'],
    ['Diesel Generator 82kVA (DG03)', 'Generators', 'Site C', 'Available', 'Now'],
    ['Dump Truck (DT12)', 'Dump Trucks', 'Site A', 'In Use', '-'],
    ['Safety Harness Set (SH08)', 'Safety Equipment', 'Site B', 'Available', 'Now'],
  ];

  readonly utilizedRows = [
    ['CAT 320 Excavator', 'Excavators', 92, '46 hrs'],
    ['ACE 14XW Crane', 'Cranes', 88, '44 hrs'],
    ['Transit Mixer 6m³', 'Concrete Mixers', 85, '43 hrs'],
    ['Tata 2518', 'Dump Trucks', 78, '39 hrs'],
    ['Diesel Generator 125kVA', 'Generators', 75, '38 hrs'],
  ];
}
