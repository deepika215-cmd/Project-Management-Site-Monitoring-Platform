import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-maintenance-scheduling',
  imports: [CommonModule],
  templateUrl: './maintenance-scheduling.html',
  styleUrl: './maintenance-scheduling.css',
})
export class MaintenanceScheduling {
  tasks = [
    { id: 'MT-2026-201', resource: 'CAT 320 Excavator', service: 'Engine Service', date: '12 Aug 2026', technician: 'M. Engineering', priority: 'Medium', status: 'Upcoming' },
    { id: 'MT-2026-202', resource: 'Transit Mixer 6m³', service: 'Drum Inspection', date: '13 Aug 2026', technician: 'Mixwell Services', priority: 'Medium', status: 'Upcoming' },
    { id: 'MT-2026-203', resource: 'ACE 14XW Crane', service: 'Hydraulic Check', date: '14 Aug 2026', technician: 'Krane Services', priority: 'High', status: 'Upcoming' },
    { id: 'MT-2026-204', resource: 'Diesel Generator 125kVA', service: 'General Service', date: '15 Aug 2026', technician: 'PowerTech', priority: 'High', status: 'Due Soon' },
    { id: 'MT-2026-205', resource: 'Tata 2518', service: 'Brake Service', date: '16 Aug 2026', technician: 'Tata Motors', priority: 'High', status: 'Due Soon' },
  ];
  complete(task: typeof this.tasks[number]) { task.status = 'Completed'; }
}
