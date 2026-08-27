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

interface ProjectOption {
  id: number;
  name: string;
}

@Component({
  selector: 'app-resource-allocation',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './resource-allocation.html',
  styleUrl: './resource-allocation.css'
})
export class ResourceAllocation implements OnInit {
  searchText = '';
  selectedCategory = '';
  resources: Resource[] = [];
  filteredResources: Resource[] = [];
  loading = false;
  loadingProjects = false;
  saving = false;
  errorMessage = '';
  notice = '';
  showResourceForm = false;
  editingResourceId: number | null = null;

  form = {
    name: '',
    type: 'Equipment',
    quantity: 1,
    status: 'Available',
    projectId: 0
  };

  readonly resourceTypes = [
    'Excavators',
    'Concrete Mixers',
    'Cranes',
    'Dump Trucks',
    'Generators',
    'Safety',
    'Equipment'
  ];

  readonly statusOptions = ['Available', 'Maintenance'];

  constructor(private api: Api) { }

  projects: ProjectOption[] = [];

  ngOnInit(): void {
    this.loadResources();
    this.loadProjects();
  }

  loadResources(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.getResources().subscribe({
      next: (items: any[]) => {
        this.resources = (items || []).map((r: any) => this.mapResource(r));
        this.filterResources();
        this.loading = false;
      },
      error: (err: any) => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load resources. Start the backend on port 8000.';
        const s = this.searchText.toLowerCase().trim();
        this.filteredResources = this.resources.filter(r =>
          (!s || r.name.toLowerCase().includes(s) || r.code.toLowerCase().includes(s) || r.category.toLowerCase().includes(s)) &&
          (!this.selectedCategory || r.category.toLowerCase() === this.selectedCategory.toLowerCase())
        );
      }
    });
  }

  loadProjects(): void {
    this.loadingProjects = true;
    this.api.getProjects().subscribe({
      next: (items: any[]) => {
        this.projects = (items || []).map((p: any) => ({ id: p.id, name: p.name }));
        this.loadingProjects = false;
      },
      error: () => {
        this.loadingProjects = false;
      }
    });
  }

  private mapResource(r: any): Resource {
    return {
      id: r.id,
      code: r.code || `RES-${r.id}`,
      name: r.name || '',
      category: r.type || r.category || 'Equipment',
      assignedProject: r.project_name || r.assignedProject || 'Unassigned',
      availability: r.status || 'Available',
      utilization: r.utilization ?? 0,
      location: r.location || '',
      quantity: r.quantity ?? 1,
      allocatedQuantity: r.allocated_quantity ?? r.allocatedQuantity ?? 0,
      projectId: r.project_id ?? r.projectId
    };
  }

  filterResources(): void {
    const s = this.searchText.toLowerCase().trim();
    this.filteredResources = this.resources.filter(r =>
      (!s || r.name.toLowerCase().includes(s) || r.code.toLowerCase().includes(s) || r.category.toLowerCase().includes(s)) &&
      (!this.selectedCategory || r.category.toLowerCase() === this.selectedCategory.toLowerCase())
    );
  }

  categories(): string[] {
    return [...new Set([...this.resourceTypes, ...this.resources.map(r => r.category)].filter(Boolean))].sort();
  }

  getAllocatedCount(): number { return this.resources.filter(r => r.allocatedQuantity > 0).length; }
  getAvailableCount(): number { return this.resources.filter(r => r.quantity - r.allocatedQuantity > 0 && !r.availability.toLowerCase().includes('maintenance')).length; }
  getMaintenanceCount(): number { return this.resources.filter(r => r.availability.toLowerCase().includes('maintenance')).length; }
  getTotalUnits(): number { return this.resources.reduce((sum, r) => sum + r.quantity, 0); }
  getAllocatedUnits(): number { return this.resources.reduce((sum, r) => sum + r.allocatedQuantity, 0); }
  getOverallUtilization(): number { const total = this.getTotalUnits(); return total ? Math.round(this.getAllocatedUnits() / total * 100) : 0; }

  getStatusClass(status: string): string {
    return String(status || 'available').toLowerCase().replace(/\s+/g, '-');
  }

  openAddResource(): void {
    this.editingResourceId = null;
    this.form = {
      name: '',
      type: 'Equipment',
      quantity: 1,
      status: 'Available',
      projectId: this.projects.length === 1 ? this.projects[0].id : 0
    };
    this.errorMessage = '';
    this.notice = '';
    this.showResourceForm = true;
  }

  openEditResource(resource: Resource): void {
    this.editingResourceId = resource.id;
    this.form = {
      name: resource.name,
      type: resource.category,
      quantity: resource.quantity,
      status: resource.availability.toLowerCase().includes('maintenance') ? 'Maintenance' : 'Available',
      projectId: Number(resource.projectId || 0)
    };
    this.errorMessage = '';
    this.notice = '';
    this.showResourceForm = true;
  }

  closeResourceForm(): void {
    if (!this.saving) this.showResourceForm = false;
  }

  saveResource(): void {
    this.errorMessage = '';
    this.notice = '';

    const name = this.form.name.trim();
    const quantity = Number(this.form.quantity);
    const projectId = Number(this.form.projectId);

    if (!name) {
      this.errorMessage = 'Enter a resource name.';
      return;
    }
    if (!Number.isInteger(quantity) || quantity < 1) {
      this.errorMessage = 'Quantity must be a whole number greater than 0.';
      return;
    }
    if (!projectId) {
      this.errorMessage = 'Select a project before saving the resource.';
      return;
    }

    const payload = {
      name,
      type: this.form.type,
      quantity,
      status: this.form.status,
      project_id: projectId
    };

    this.saving = true;
    const request = this.editingResourceId === null
      ? this.api.createResource(payload)
      : this.api.updateResource(this.editingResourceId, payload);

    request.subscribe({
      next: () => {
        this.saving = false;
        this.showResourceForm = false;
        this.notice = this.editingResourceId === null
          ? `${name} was added successfully.`
          : `${name} was updated successfully.`;
        this.loadResources();
      },
      error: (err: any) => {
        this.saving = false;
        const detail = err?.error?.detail;
        this.errorMessage = Array.isArray(detail)
          ? detail.map((item: any) => item?.msg || 'Invalid value').join(', ')
          : detail || `Unable to ${this.editingResourceId === null ? 'add' : 'update'} the resource.`;
      }
    });
  }

  allocate(resource: Resource): void {
    if (resource.availability.toLowerCase().includes('maintenance')) {
      this.notice = `${resource.name} is in maintenance and cannot be allocated.`;
      return;
    }
    const available = resource.quantity - resource.allocatedQuantity;
    if (available <= 0) { this.notice = `${resource.name} has no available units.`; return; }
    const value = window.prompt(`Quantity to allocate (available: ${available})`, '1');
    const quantity = Number(value);
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > available) {
      if (value !== null) this.notice = `Enter a whole number from 1 to ${available}.`;
      return;
    }
    this.api.allocateResource(resource.id, { quantity }).subscribe({
      next: () => { this.notice = `${quantity} unit(s) allocated from ${resource.name}.`; this.loadResources(); },
      error: (err: any) => this.notice = err?.error?.detail || 'Allocation failed.'
    });
  }

  release(resource: Resource): void {
    if (resource.allocatedQuantity <= 0) { this.notice = `${resource.name} has no allocated units.`; return; }
    const value = window.prompt(`Quantity to release (allocated: ${resource.allocatedQuantity})`, '1');
    const quantity = Number(value);
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > resource.allocatedQuantity) {
      if (value !== null) this.notice = `Enter a whole number from 1 to ${resource.allocatedQuantity}.`;
      return;
    }
    this.api.releaseResource(resource.id, quantity).subscribe({
      next: () => { this.notice = `${quantity} unit(s) released from ${resource.name}.`; this.loadResources(); },
      error: (err: any) => this.notice = err?.error?.detail || 'Release failed.'
    });
  }
}
