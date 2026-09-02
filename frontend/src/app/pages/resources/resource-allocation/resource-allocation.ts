import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';
import { Api } from '../../../services/api';

interface Resource {
  id: number;
  code: string;
  name: string;
  category: string;
  assignedProject: string;
  availability: string;
  utilization: number;
  location: string;
  quantity: number;
  allocatedQuantity: number;
  projectId?: number;
}
interface ProjectOption { id: number; name: string; }
interface Maintenance { id: number; resourceId: number; resourceName: string; date: string; type: string; status: string; notes: string; }

@Component({
  selector: 'app-resource-allocation',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './resource-allocation.html',
  styleUrl: './resource-allocation.css'
})
export class ResourceAllocation implements OnInit {
  resources: Resource[] = [];
  filteredResources: Resource[] = [];
  projects: ProjectOption[] = [];
  searchText = '';
  selectedCategory = '';
  loading = false;
  saving = false;
  errorMessage = '';
  notice = '';
  showMaintenanceForm = false;
  showResourceForm = false;
  editingResourceId: number | null = null;
  maintenanceRecords: Maintenance[] = [];

  readonly resourceCategories = ['Excavators', 'Concrete Mixers', 'Cranes', 'Dump Trucks', 'Generators', 'Safety Equipment'];
  readonly resourceStatuses = ['Available', 'Partially Allocated', 'Fully Allocated', 'Maintenance'];

  resourceForm: any = {
    name: '', type: 'Excavators', quantity: 1, status: 'Available', project_id: 0
  };
  maintenanceForm: any = {
    resourceId: 0, resourceName: '', date: '', type: 'Routine Service', status: 'Scheduled', notes: ''
  };

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadMaintenance();
    this.loadProjects();
    this.loadResources();
  }

  loadProjects() {
    this.api.getProjects().subscribe({
      next: (rows: any[]) => {
        this.projects = (rows || []).map(p => ({ id: +p.id, name: p.name || p.project_name || `Project #${p.id}` }));
        if (!this.resourceForm.project_id && this.projects.length) this.resourceForm.project_id = this.projects[0].id;
      },
      error: () => { this.projects = []; }
    });
  }

  loadResources() {
    this.loading = true;
    this.errorMessage = '';
    this.api.getResources().subscribe({
      next: (rows: any[]) => {
        this.resources = (rows || []).map(r => ({
          id: +r.id,
          code: `RES-${String(r.id).padStart(3, '0')}`,
          name: r.name || 'Unnamed resource',
          category: r.type || r.category || 'Equipment',
          assignedProject: r.project_id ? `Project #${r.project_id}` : 'Unassigned',
          availability: r.status || (+(r.allocated_quantity || 0) >= +(r.quantity || 0) ? 'Fully Allocated' : 'Available'),
          utilization: +r.quantity ? Math.min(100, Math.round((+(r.allocated_quantity || 0) / +r.quantity) * 100)) : 0,
          location: r.location || 'Site',
          quantity: +(r.quantity || 0),
          allocatedQuantity: +(r.allocated_quantity || 0),
          projectId: r.project_id
        }));
        this.filterResources();
        this.loading = false;
      },
      error: e => {
        this.loading = false;
        this.errorMessage = e?.error?.detail || 'Unable to load resources. Start the backend on port 8000.';
      }
    });
  }

  filterResources() {
    const s = this.searchText.toLowerCase().trim();
    this.filteredResources = this.resources.filter(r =>
      (!s || r.name.toLowerCase().includes(s) || r.code.toLowerCase().includes(s) || r.category.toLowerCase().includes(s)) &&
      (!this.selectedCategory || r.category.toLowerCase() === this.selectedCategory.toLowerCase())
    );
  }

  categories() { return this.resourceCategories; }
  getAllocatedCount() { return this.resources.filter(r => r.allocatedQuantity > 0).length; }
  getAvailableCount() { return this.resources.filter(r => r.quantity - r.allocatedQuantity > 0 && r.availability !== 'Maintenance').length; }
  getMaintenanceCount() { return this.maintenanceRecords.filter(r => r.status !== 'Completed').length + this.resources.filter(r => r.availability === 'Maintenance').length; }
  getTotalUnits() { return this.resources.reduce((s, r) => s + r.quantity, 0); }
  getAllocatedUnits() { return this.resources.reduce((s, r) => s + r.allocatedQuantity, 0); }
  getOverallUtilization() { const t = this.getTotalUnits(); return t ? Math.round(this.getAllocatedUnits() / t * 100) : 0; }
  getStatusClass(s: string) { return String(s || 'available').toLowerCase().replace(/\s+/g, '-'); }

  openCreateResource() {
    this.editingResourceId = null;
    this.resourceForm = { name: '', type: 'Excavators', quantity: 1, status: 'Available', project_id: this.projects[0]?.id || 0 };
    this.showResourceForm = true;
    this.notice = '';
  }

  editResource(r: Resource) {
    this.editingResourceId = r.id;
    this.resourceForm = {
      name: r.name,
      type: this.resourceCategories.includes(r.category) ? r.category : r.category,
      quantity: r.quantity,
      status: r.availability === 'Partially Allocated' || r.availability === 'Fully Allocated' ? r.availability : r.availability,
      project_id: r.projectId || this.projects[0]?.id || 0
    };
    this.showResourceForm = true;
    this.notice = '';
  }

  saveResource() {
    const name = String(this.resourceForm.name || '').trim();
    const quantity = Number(this.resourceForm.quantity);
    const projectId = Number(this.resourceForm.project_id);
    if (!name || !Number.isInteger(quantity) || quantity < 1) {
      this.notice = 'Enter a resource name and a whole quantity of at least 1.';
      return;
    }
    if (!projectId) {
      this.notice = 'Select a project before saving the resource.';
      return;
    }

    const payload = {
      name,
      type: this.resourceForm.type,
      quantity,
      status: this.resourceForm.status || 'Available',
      project_id: projectId
    };
    this.saving = true;
    const request = this.editingResourceId
      ? this.api.updateResource(this.editingResourceId, payload)
      : this.api.createResource(payload);

    request.subscribe({
      next: () => {
        this.saving = false;
        this.showResourceForm = false;
        this.notice = this.editingResourceId ? `${name} updated successfully.` : `${name} added successfully.`;
        this.loadResources();
      },
      error: e => {
        this.saving = false;
        this.notice = e?.error?.detail || 'Unable to save the resource.';
      }
    });
  }

  cancelResourceForm() { this.showResourceForm = false; this.editingResourceId = null; }

  markMaintenance(r: Resource) {
    if (r.allocatedQuantity > 0) {
      this.notice = `${r.name} has ${r.allocatedQuantity} allocated unit(s). Release them before putting the resource into maintenance.`;
      return;
    }
    const projectId = r.projectId || this.projects[0]?.id;
    if (!projectId) { this.notice = 'A project is required by the backend resource API.'; return; }
    this.api.updateResource(r.id, {
      name: r.name,
      type: r.category,
      quantity: r.quantity,
      status: 'Maintenance',
      project_id: projectId
    }).subscribe({
      next: () => { this.notice = `${r.name} is now marked as Maintenance.`; this.loadResources(); },
      error: e => this.notice = e?.error?.detail || 'Unable to mark the resource as maintenance.'
    });
  }

  markAvailable(r: Resource) {
    const projectId = r.projectId || this.projects[0]?.id;
    if (!projectId) { this.notice = 'A project is required by the backend resource API.'; return; }
    this.api.updateResource(r.id, {
      name: r.name,
      type: r.category,
      quantity: r.quantity,
      status: r.allocatedQuantity > 0 ? 'Partially Allocated' : 'Available',
      project_id: projectId
    }).subscribe({
      next: () => { this.notice = `${r.name} is available again.`; this.loadResources(); },
      error: e => this.notice = e?.error?.detail || 'Unable to update resource status.'
    });
  }

  allocate(r: Resource) {
    if (r.availability === 'Maintenance') { this.notice = `${r.name} is in maintenance and cannot be allocated.`; return; }
    const a = r.quantity - r.allocatedQuantity;
    if (a <= 0) { this.notice = `${r.name} has no available units.`; return; }
    const v = prompt(`Quantity to allocate (available: ${a})`, '1');
    const q = Number(v);
    if (!Number.isInteger(q) || q < 1 || q > a) { if (v !== null) this.notice = `Enter a whole number from 1 to ${a}.`; return; }
    this.api.allocateResource(r.id, { quantity: q }).subscribe({
      next: () => { this.notice = `${q} unit(s) allocated from ${r.name}.`; this.loadResources(); },
      error: e => this.notice = e?.error?.detail || 'Allocation failed.'
    });
  }

  release(r: Resource) {
    if (r.allocatedQuantity <= 0) { this.notice = `${r.name} has no allocated units.`; return; }
    const v = prompt(`Quantity to release (allocated: ${r.allocatedQuantity})`, '1');
    const q = Number(v);
    if (!Number.isInteger(q) || q < 1 || q > r.allocatedQuantity) { if (v !== null) this.notice = `Enter a whole number from 1 to ${r.allocatedQuantity}.`; return; }
    this.api.releaseResource(r.id, q).subscribe({
      next: () => { this.notice = `${q} unit(s) released from ${r.name}.`; this.loadResources(); },
      error: e => this.notice = e?.error?.detail || 'Release failed.'
    });
  }

  openMaintenance(r?: Resource) {
    const x = r || this.resources[0];
    if (!x) { this.notice = 'Load a resource before scheduling maintenance.'; return; }
    this.maintenanceForm = { resourceId: x.id, resourceName: x.name, date: new Date().toISOString().slice(0, 10), type: 'Routine Service', status: 'Scheduled', notes: '' };
    this.showMaintenanceForm = true;
  }

  resourceChanged() {
    const r = this.resources.find(x => x.id === +this.maintenanceForm.resourceId);
    this.maintenanceForm.resourceName = r?.name || '';
  }

  saveMaintenance() {
    if (!this.maintenanceForm.resourceId || !this.maintenanceForm.date) { this.notice = 'Select a resource and maintenance date.'; return; }
    const id = this.maintenanceRecords.reduce((m, r) => Math.max(m, r.id), 0) + 1;
    this.maintenanceRecords.push({ id, ...this.maintenanceForm });
    localStorage.setItem('buildtrack_resource_maintenance', JSON.stringify(this.maintenanceRecords));
    const r = this.resources.find(x => x.id === +this.maintenanceForm.resourceId);
    if (r && r.allocatedQuantity === 0 && this.maintenanceForm.status !== 'Completed') this.markMaintenance(r);
    this.showMaintenanceForm = false;
    this.notice = 'Maintenance schedule saved. The resource is marked Maintenance when it has no allocated units.';
  }

  deleteMaintenance(id: number) {
    this.maintenanceRecords = this.maintenanceRecords.filter(r => r.id !== id);
    localStorage.setItem('buildtrack_resource_maintenance', JSON.stringify(this.maintenanceRecords));
  }

  loadMaintenance() {
    try { this.maintenanceRecords = JSON.parse(localStorage.getItem('buildtrack_resource_maintenance') || '[]') || []; }
    catch { this.maintenanceRecords = []; }
  }
}
