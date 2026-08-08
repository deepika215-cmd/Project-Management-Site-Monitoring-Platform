import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

interface Project {
  id: number;
  code: string;
  name: string;
  category: string;
  manager: string;
  budget: number;
  startDate: string;
  progress: number;
  status: string;
}

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './project-list.html',
  styleUrl: './project-list.css'
})
export class ProjectList {

  searchText = '';

  selectedCategory = '';

  selectedStatus = '';


  projects: Project[] = [

    {
      id: 1,
      code: 'BT-001',
      name: 'Green Valley Apartments',
      category: 'Residential',
      manager: 'Raj Kumar',
      budget: 5000000,
      startDate: '2026-01-15',
      progress: 65,
      status: 'In Progress'
    },

    {
      id: 2,
      code: 'BT-002',
      name: 'City Mall Construction',
      category: 'Commercial',
      manager: 'Arun Kumar',
      budget: 8500000,
      startDate: '2026-03-01',
      progress: 10,
      status: 'Planning'
    },

    {
      id: 3,
      code: 'BT-003',
      name: 'National Highway Project',
      category: 'Infrastructure',
      manager: 'Vijay Kumar',
      budget: 15000000,
      startDate: '2025-02-10',
      progress: 100,
      status: 'Completed'
    },

    {
      id: 4,
      code: 'BT-004',
      name: 'Tech Park Development',
      category: 'Commercial',
      manager: 'Suresh Kumar',
      budget: 12000000,
      startDate: '2026-02-20',
      progress: 40,
      status: 'In Progress'
    },

    {
      id: 5,
      code: 'BT-005',
      name: 'Government School Project',
      category: 'Government',
      manager: 'Ravi Kumar',
      budget: 3000000,
      startDate: '2026-04-05',
      progress: 5,
      status: 'Planning'
    },

    {
      id: 6,
      code: 'BT-006',
      name: 'Industrial Warehouse',
      category: 'Industrial',
      manager: 'Karthik Kumar',
      budget: 7000000,
      startDate: '2025-11-15',
      progress: 75,
      status: 'In Progress'
    },

    {
      id: 7,
      code: 'BT-007',
      name: 'Metro Infrastructure Project',
      category: 'Infrastructure',
      manager: 'Prakash Kumar',
      budget: 20000000,
      startDate: '2025-05-10',
      progress: 55,
      status: 'On Hold'
    }

  ];


  filteredProjects: Project[] = [...this.projects];


  filterProjects(): void {

    const search = this.searchText
      .toLowerCase()
      .trim();


    this.filteredProjects = this.projects.filter(project => {

      const matchesSearch =
        project.name.toLowerCase().includes(search) ||
        project.code.toLowerCase().includes(search);


      const matchesCategory =
        !this.selectedCategory ||
        project.category === this.selectedCategory;


      const matchesStatus =
        !this.selectedStatus ||
        project.status === this.selectedStatus;


      return (
        matchesSearch &&
        matchesCategory &&
        matchesStatus
      );

    });

  }


  getProjectCount(status: string): number {

    return this.projects.filter(
      project => project.status === status
    ).length;

  }


  getStatusClass(status: string): string {

    switch (status) {

      case 'Planning':
        return 'planning';

      case 'In Progress':
        return 'in-progress';

      case 'On Hold':
        return 'on-hold';

      case 'Completed':
        return 'completed';

      case 'Closed':
        return 'closed';

      default:
        return '';

    }

  }

}