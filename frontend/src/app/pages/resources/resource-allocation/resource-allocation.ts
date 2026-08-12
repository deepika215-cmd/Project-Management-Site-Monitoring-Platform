<<<<<<< HEAD
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Api } from '../../../services/api';

interface Resource { id: number; code: string; name: string; category: string; assignedProject: string; availability: string; utilization: number; location: string; quantity: number; allocatedQuantity: number; projectId: number; }

@Component({ selector: 'app-resource-allocation', standalone: true, imports: [CommonModule, FormsModule, RouterLink], templateUrl: './resource-allocation.html', styleUrl: './resource-allocation.css' })
export class ResourceAllocation implements OnInit {
  searchText = ''; selectedCategory = ''; resources: Resource[] = []; filteredResources: Resource[] = []; loading = false; errorMessage = '';
  constructor(private api: Api) {}
  ngOnInit(): void { this.loadResources(); }

  loadResources(): void {
    this.loading = true;
    this.api.getResources().subscribe({
      next: (items: any[]) => {
        this.resources = (items || []).map(r => ({ id: r.id, code: `RES-${String(r.id).padStart(3,'0')}`, name: r.name, category: r.type, assignedProject: r.project_id ? `Project #${r.project_id}` : 'Unassigned', availability: r.status, utilization: r.quantity ? Math.round(r.allocated_quantity / r.quantity * 100) : 0, location: 'Backend data', quantity: r.quantity, allocatedQuantity: r.allocated_quantity, projectId: r.project_id }));
        this.filterResources(); this.loading = false;
      },
      error: err => { this.loading = false; this.errorMessage = err?.error?.detail || 'Unable to load resources.'; }
    });
  }
  filterResources(): void { const s = this.searchText.toLowerCase().trim(); this.filteredResources = this.resources.filter(r => (!s || r.name.toLowerCase().includes(s) || r.code.toLowerCase().includes(s)) && (!this.selectedCategory || r.category === this.selectedCategory)); }
  getStatusClass(status: string): string { return status.toLowerCase().replace(/\s+/g,'-'); }
  getAllocatedCount(): number { return this.resources.filter(r => r.allocatedQuantity > 0).length; }
  getAvailableCount(): number { return this.resources.filter(r => r.quantity - r.allocatedQuantity > 0).length; }
  getMaintenanceCount(): number { return this.resources.filter(r => r.availability.toLowerCase().includes('maintenance')).length; }
  allocate(resource: Resource): void { const available = resource.quantity - resource.allocatedQuantity; const quantity = Number(prompt(`Quantity to allocate (available: ${available})`, '1')); if (!quantity || quantity < 1) return; this.api.allocateResource(resource.id, { quantity }).subscribe({ next: () => this.loadResources(), error: err => this.errorMessage = err?.error?.detail || 'Allocation failed.' }); }
  release(resource: Resource): void { if (resource.allocatedQuantity <= 0) return; const quantity = Number(prompt(`Quantity to release (allocated: ${resource.allocatedQuantity})`, '1')); if (!quantity || quantity < 1) return; this.api.releaseResource(resource.id, quantity).subscribe({ next: () => this.loadResources(), error: err => this.errorMessage = err?.error?.detail || 'Release failed.' }); }
}
=======
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

interface Resource {

  id: number;
  code: string;
  name: string;
  category: string;
  assignedProject: string;
  availability: string;
  utilization: number;
  location: string;

}

@Component({
  selector: 'app-resource-allocation',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './resource-allocation.html',
  styleUrl: './resource-allocation.css'
})

export class ResourceAllocation {

  searchText = '';

  selectedCategory = '';

  resources: Resource[] = [

    {
      id: 1,
      code: 'EQ-001',
      name: 'Excavator CAT320',
      category: 'Machinery',
      assignedProject: 'Green Valley Apartments',
      availability: 'Allocated',
      utilization: 85,
      location: 'Site A'
    },

    {
      id: 2,
      code: 'EQ-002',
      name: 'Tower Crane',
      category: 'Machinery',
      assignedProject: 'City Mall Construction',
      availability: 'Allocated',
      utilization: 70,
      location: 'Site B'
    },

    {
      id: 3,
      code: 'EQ-003',
      name: 'Concrete Mixer',
      category: 'Equipment',
      assignedProject: 'Metro Infrastructure',
      availability: 'Available',
      utilization: 20,
      location: 'Warehouse'
    },

    {
      id: 4,
      code: 'EQ-004',
      name: 'Dump Truck',
      category: 'Vehicle',
      assignedProject: 'Industrial Warehouse',
      availability: 'Maintenance',
      utilization: 0,
      location: 'Service Center'
    },

    {
      id: 5,
      code: 'EQ-005',
      name: 'Generator',
      category: 'Electrical',
      assignedProject: 'Government School',
      availability: 'Allocated',
      utilization: 60,
      location: 'Site C'
    }

  ];

  filteredResources: Resource[] = [...this.resources];

  filterResources() {

    const search = this.searchText.toLowerCase();

    this.filteredResources = this.resources.filter(resource => {

      const matchesSearch =
        resource.name.toLowerCase().includes(search) ||
        resource.code.toLowerCase().includes(search);

      const matchesCategory =
        !this.selectedCategory ||
        resource.category === this.selectedCategory;

      return matchesSearch && matchesCategory;

    });

  }

  getStatusClass(status: string): string {

    switch (status) {

      case 'Allocated':
        return 'allocated';

      case 'Available':
        return 'available';

      case 'Maintenance':
        return 'maintenance';

      default:
        return '';

    }

  }

  getAllocatedCount() {

    return this.resources.filter(
      x => x.availability === 'Allocated'
    ).length;

  }

  getAvailableCount() {

    return this.resources.filter(
      x => x.availability === 'Available'
    ).length;

  }

  getMaintenanceCount() {

    return this.resources.filter(
      x => x.availability === 'Maintenance'
    ).length;

  }

}
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
