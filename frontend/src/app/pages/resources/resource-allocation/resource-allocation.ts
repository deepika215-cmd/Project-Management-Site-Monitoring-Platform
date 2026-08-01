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