import { CommonModule } from '@angular/common';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-resource-operations',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './resource-operations.html',
  styleUrl: './resource-operations.css'
})
export class ResourceOperations implements OnInit {
  projects: any[] = [];
  machinery: any[] = [];
  maintenance: any[] = [];
  resources: any[] = [];
  loading = false;
  saving = false;
  error = '';
  message = '';
  tab: 'tracking'|'maintenance'|'utilization' = 'tracking';
  types = ['Excavator','Concrete Mixer','Crane','Dump Truck','Generator','Safety Equipment'];
  today = new Date().toISOString().slice(0,10);
  machine: any = this.emptyMachine();
  maintenanceForm: any = this.emptyMaintenance();

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true;
    this.error = '';
    forkJoin({
      projects: this.api.getProjects().pipe(timeout(9000), catchError(() => of([] as any[]))),
      machinery: this.api.getMachinery().pipe(timeout(9000), catchError(() => of([] as any[]))),
      maintenance: this.api.getMaintenance().pipe(timeout(9000), catchError(() => of([] as any[]))),
      resources: this.api.getResources().pipe(timeout(9000), catchError(() => of([] as any[])))
    }).pipe(finalize(() => { this.loading = false; this.cdr.detectChanges(); }))
      .subscribe(r => {
        this.projects = r.projects || [];
        this.machinery = r.machinery || [];
        this.maintenance = r.maintenance || [];
        this.resources = r.resources || [];
        if (!this.maintenanceForm.machinery_id) this.maintenanceForm.machinery_id = Number(this.machinery[0]?.id || 0);
      });
  }

  project(id: any): string { return id ? this.projects.find(p => Number(p.id) === Number(id))?.project_name || `Project #${id}` : 'Equipment Yard'; }
  machineName(id: any): string { return this.machinery.find(m => Number(m.id) === Number(id))?.name || `Machine #${id}`; }

  addMachine(): void {
    if (!this.machine.name.trim()) { this.error = 'Equipment name is required.'; return; }
    this.saving = true;
    this.error = '';
    this.message = '';
    this.api.createMachinery({ ...this.machine, project_id: this.machine.project_id || null }).pipe(
      timeout(10000),
      finalize(() => { this.saving = false; this.cdr.detectChanges(); })
    ).subscribe({
      next: (created: any) => {
        if (created?.id) this.machinery = [created, ...this.machinery.filter(m => Number(m.id) !== Number(created.id))];
        this.message = 'Machinery added.';
        this.machine = this.emptyMachine();
        this.load();
      },
      error: e => this.error = this.detail(e, 'Unable to add machinery.')
    });
  }

  setStatus(m: any, status: string): void {
    this.api.updateMachineryStatus(m.id, status).pipe(timeout(10000)).subscribe({
      next: (updated: any) => { Object.assign(m, updated || { status }); this.message = 'Machinery status updated.'; },
      error: e => this.error = this.detail(e, 'Status update failed.')
    });
  }

  addHours(m: any): void {
    const raw = prompt(`Add operating hours for ${m.name}`, '1');
    if (raw === null) return;
    const hours = Number(raw);
    if (!(hours > 0)) return;
    this.api.addMachineryHours(m.id, hours).pipe(timeout(10000)).subscribe({
      next: (updated: any) => { Object.assign(m, updated || { hours_used: Number(m.hours_used || 0) + hours }); this.message = 'Operating hours updated.'; },
      error: e => this.error = this.detail(e, 'Unable to update operating hours.')
    });
  }

  schedule(): void {
    if (!this.maintenanceForm.machinery_id) { this.error = 'Select equipment.'; return; }
    this.saving = true;
    this.error = '';
    this.message = '';
    this.api.createMaintenance({ ...this.maintenanceForm, completion_date: this.maintenanceForm.completion_date || null }).pipe(
      timeout(10000),
      finalize(() => { this.saving = false; this.cdr.detectChanges(); })
    ).subscribe({
      next: (created: any) => { if (created?.id) this.maintenance = [created, ...this.maintenance]; this.message = 'Maintenance scheduled.'; this.load(); },
      error: e => this.error = this.detail(e, 'Unable to schedule maintenance.')
    });
  }

  complete(m: any): void {
    this.api.completeMaintenance(m.id, this.today).pipe(timeout(10000)).subscribe({
      next: (updated: any) => { Object.assign(m, updated || { status: 'Completed', completion_date: this.today }); this.message = 'Maintenance marked completed.'; },
      error: e => this.error = this.detail(e, 'Unable to complete maintenance.')
    });
  }

  totalUnits(): number { return this.resources.reduce((s, r) => s + Number(r.quantity || 0), 0); }
  allocatedUnits(): number { return this.resources.reduce((s, r) => s + Number(r.allocated_quantity || r.allocatedQuantity || 0), 0); }
  utilization(): number { const t = this.totalUnits(); return t ? Math.round(this.allocatedUnits() / t * 100) : 0; }
  availableMachines(): number { return this.machinery.filter(m => String(m.status).toLowerCase() === 'available').length; }
  maintenanceMachines(): number { return this.machinery.filter(m => String(m.status).toLowerCase().includes('maintenance')).length; }
  resourcePct(r: any): number { const q = Number(r.quantity || 0); return q ? Math.round(Number(r.allocated_quantity ?? r.allocatedQuantity ?? 0) / q * 100) : 0; }

  private emptyMachine(): any { return { equipment_id: '', name: '', machinery_type: 'Excavator', location: 'Equipment Yard', status: 'Available', operator: '', hours_used: 0, project_id: null }; }
  private emptyMaintenance(): any { return { machinery_id: 0, maintenance_type: 'Preventive', description: '', scheduled_date: this.today, completion_date: null, status: 'Scheduled', cost: 0, technician: '' }; }
  private detail(e: any, fallback: string): string {
    const d = e?.error?.detail ?? e?.error?.message ?? e?.message;
    return Array.isArray(d) ? d.map((x: any) => x?.msg || String(x)).join(', ') : d || fallback;
  }
}
