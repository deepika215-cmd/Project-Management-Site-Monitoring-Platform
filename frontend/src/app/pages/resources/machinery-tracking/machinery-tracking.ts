import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-machinery-tracking',
  imports: [CommonModule],
  templateUrl: './machinery-tracking.html',
  styleUrl: './machinery-tracking.css',
})
export class MachineryTracking {
  filter = 'All';
  machines = [
    { code: 'EQ-001', name: 'CAT 320 Excavator', type: 'Excavator', location: 'Site A - Block 3', operator: 'Ramesh Kumar', hours: 46, fuel: 78, status: 'Operating' },
    { code: 'EQ-014', name: 'ACE 14XW Crane', type: 'Crane', location: 'Site B - Tower 2', operator: 'Amit Singh', hours: 44, fuel: 62, status: 'Operating' },
    { code: 'EQ-022', name: 'Transit Mixer 6m³', type: 'Mixer', location: 'Site A - Batching Plant', operator: 'Sanjay Verma', hours: 43, fuel: 51, status: 'Idle' },
    { code: 'EQ-031', name: 'Tata 2518 Dump Truck', type: 'Vehicle', location: 'Site C - Access Road', operator: 'Vikram Yadav', hours: 39, fuel: 35, status: 'Maintenance' },
    { code: 'EQ-042', name: 'Diesel Generator 125kVA', type: 'Generator', location: 'Site B - Tower 1', operator: 'Unassigned', hours: 38, fuel: 88, status: 'Idle' },
  ];
  get filteredMachines() { return this.filter === 'All' ? this.machines : this.machines.filter(item => item.status === this.filter); }
  update(machine: typeof this.machines[number]) { machine.status = machine.status === 'Operating' ? 'Idle' : 'Operating'; }
}
