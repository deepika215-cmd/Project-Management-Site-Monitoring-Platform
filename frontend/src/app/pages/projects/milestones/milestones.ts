<<<<<<< HEAD
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';
=======
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946

interface Milestone {
  id: number;
  name: string;
  description: string;
  plannedDate: string;
  actualDate: string | null;
  status: string;
<<<<<<< HEAD
  projectId: number;
=======
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
}

@Component({
  selector: 'app-milestones',
  standalone: true,
<<<<<<< HEAD
  imports: [CommonModule, FormsModule, RouterLink, AppSidebarComponent],
  templateUrl: './milestones.html',
  styleUrl: './milestones.css'
})
export class Milestones implements OnInit {
  selectedProject = 0;
  projects: any[] = [];
  milestones: Milestone[] = [];
  editingMilestoneId: number | null = null;
  showAddModal = false;
  loading = false;
  loadingProjects = false;
  errorMessage = '';
  successMessage = '';
  editForm = { name: '', description: '', plannedDate: '', status: 'Pending' };
  newMilestone = { name: '', description: '', plannedDate: '', status: 'Pending' };

  constructor(private api: Api, private route: ActivatedRoute, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      const requestedId = Number(params.get('projectId') || 0);
      this.loadProjects(requestedId);
    });
  }

  loadProjects(preferredId = 0): void {
    this.loadingProjects = true;
    this.errorMessage = '';
    this.api.getProjects().subscribe({
      next: (projects: any[]) => {
        this.projects = Array.isArray(projects) ? projects : [];
        const requestedExists = this.projects.some(project => Number(project.id) === Number(preferredId));
        this.selectedProject = requestedExists ? Number(preferredId) : Number(this.projects[0]?.id || 0);
        this.loadingProjects = false;
        this.loadMilestones();
        this.cdr.detectChanges();
      },
      error: err => {
        this.loadingProjects = false;
        this.projects = [];
        this.milestones = [];
        this.errorMessage = err?.error?.detail || 'Unable to load projects from the backend.';
        this.cdr.detectChanges();
      }
    });
  }

  loadMilestones(): void {
    if (!this.selectedProject) { this.milestones = []; return; }
    this.loading = true;
    this.errorMessage = '';
    this.api.getMilestones().subscribe({
      next: (items: any[]) => {
        const rows = Array.isArray(items) ? items : [];
        this.milestones = rows
          .filter(item => Number(item.project_id) === Number(this.selectedProject))
          .map(item => ({
            id: Number(item.id), name: item.title || '', description: item.description || '',
            plannedDate: item.due_date || '', actualDate: item.status === 'Completed' ? item.due_date : null,
            status: item.status || 'Pending', projectId: Number(item.project_id)
          }));
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: err => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Unable to load milestones.';
        this.cdr.detectChanges();
      }
    });
  }

  onProjectChange(): void {
    this.selectedProject = Number(this.selectedProject);
    this.editingMilestoneId = null;
    this.closeAddMilestone();
    this.loadMilestones();
  }

  get completedPercentage(): number {
    return this.milestones.length ? Math.round(this.milestones.filter(m => m.status === 'Completed').length / this.milestones.length * 100) : 0;
  }

  getStatusCount(status: string): number { return this.milestones.filter(m => m.status === status).length; }
  getStatusClass(status: string): string { return status.toLowerCase().replace(/\s+/g, '-'); }
  getDelayedCount(): number { return this.milestones.filter(m => this.isDelayed(m)).length; }
  isDelayed(m: Milestone): boolean { return m.status !== 'Completed' && !!m.plannedDate && new Date() > new Date(m.plannedDate); }

  openAddMilestone(): void {
    if (!this.selectedProject) return;
    this.errorMessage = '';
    this.successMessage = '';
    this.newMilestone = { name: '', description: '', plannedDate: '', status: 'Pending' };
    this.showAddModal = true;
  }

  closeAddMilestone(): void { this.showAddModal = false; }

  addMilestone(): void {
    if (!this.selectedProject || !this.newMilestone.name.trim() || !this.newMilestone.plannedDate) {
      this.errorMessage = 'Milestone title and due date are required.';
      return;
    }
    this.loading = true;
    this.errorMessage = '';
    this.api.createMilestone({
      title: this.newMilestone.name.trim(),
      description: this.newMilestone.description.trim() || 'No description provided',
      due_date: this.newMilestone.plannedDate,
      status: this.newMilestone.status,
      project_id: Number(this.selectedProject)
    }).subscribe({
      next: created => {
        this.closeAddMilestone();
        this.loading = false;
        this.successMessage = `Milestone "${created?.title || this.newMilestone.name}" was added successfully.`;
        this.loadMilestones();
        this.cdr.detectChanges();
      },
      error: err => { this.loading = false; this.errorMessage = this.getError(err, 'Unable to create milestone.'); this.cdr.detectChanges(); }
    });
  }

  startEdit(m: Milestone): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.editingMilestoneId = m.id;
    this.editForm = { name: m.name, description: m.description, plannedDate: m.plannedDate, status: m.status };
  }

  saveEdit(m: Milestone): void {
    if (!this.editForm.name.trim() || !this.editForm.plannedDate) {
      this.errorMessage = 'Milestone title and due date are required.';
      return;
    }
    this.loading = true;
    this.api.updateMilestone(m.id, {
      title: this.editForm.name.trim(), description: this.editForm.description.trim() || 'No description provided',
      due_date: this.editForm.plannedDate, status: this.editForm.status, project_id: m.projectId
    }).subscribe({
      next: () => { this.editingMilestoneId = null; this.loading = false; this.loadMilestones(); this.cdr.detectChanges(); },
      error: err => { this.loading = false; this.errorMessage = this.getError(err, 'Unable to update milestone.'); this.cdr.detectChanges(); }
    });
  }

  cancelEdit(): void { this.editingMilestoneId = null; }

  deleteMilestone(id: number): void {
    this.successMessage = '';
    if (!confirm('Are you sure you want to delete this milestone?')) return;
    this.loading = true;
    this.api.deleteMilestone(id).subscribe({
      next: () => { this.successMessage = 'Milestone deleted successfully.'; this.loadMilestones(); this.cdr.detectChanges(); },
      error: err => { this.loading = false; this.errorMessage = this.getError(err, 'Unable to delete milestone.'); this.cdr.detectChanges(); }
    });
  }
  private getError(err: any, fallback: string): string {
    const detail = err?.error?.detail;
    if (Array.isArray(detail)) return detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
    return detail || fallback;
  }
}
=======
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './milestones.html',
  styleUrl: './milestones.css'
})
export class Milestones {

  selectedProject = 'BT-001';

  editingMilestoneId: number | null = null;

  editForm = {
    name: '',
    description: '',
    plannedDate: '',
    status: ''
  };

  // ===== Modal =====

  showAddModal = false;

  newMilestone = {
    name: '',
    description: '',
    plannedDate: '',
    status: 'Pending'
  };

  milestones: Milestone[] = [
    {
      id: 1,
      name: 'Foundation Completed',
      description:
        'Completion of foundation and underground structural work.',
      plannedDate: '2026-03-15',
      actualDate: '2026-03-12',
      status: 'Completed'
    },
    {
      id: 2,
      name: 'Structural Work Completed',
      description:
        'Completion of major structural construction activities.',
      plannedDate: '2026-07-30',
      actualDate: null,
      status: 'In Progress'
    },
    {
      id: 3,
      name: 'Electrical Work Completed',
      description:
        'Completion of electrical wiring and installations.',
      plannedDate: '2026-10-30',
      actualDate: null,
      status: 'Pending'
    },
    {
      id: 4,
      name: 'Plumbing Completed',
      description:
        'Completion of plumbing and water supply systems.',
      plannedDate: '2026-11-30',
      actualDate: null,
      status: 'Pending'
    }
  ];

  get completedPercentage(): number {
    if (this.milestones.length === 0) {
      return 0;
    }

    const completed = this.milestones.filter(
      m => m.status === 'Completed'
    ).length;

    return Math.round((completed / this.milestones.length) * 100);
  }

  getStatusCount(status: string): number {
    return this.milestones.filter(
      m => m.status === status
    ).length;
  }

  getDelayedCount(): number {
    return this.milestones.filter(
      m => this.isDelayed(m)
    ).length;
  }

  isDelayed(milestone: Milestone): boolean {

    if (milestone.status === 'Completed') {
      return false;
    }

    return new Date() > new Date(milestone.plannedDate);
  }
    // ============================
  // ADD MILESTONE MODAL
  // ============================

  openAddMilestone(): void {
    this.newMilestone = {
      name: '',
      description: '',
      plannedDate: '',
      status: 'Pending'
    };

    this.showAddModal = true;
  }

  closeAddMilestone(): void {
    this.showAddModal = false;
  }

  addMilestone(): void {

    if (
      !this.newMilestone.name.trim() ||
      !this.newMilestone.plannedDate
    ) {
      return;
    }

    const milestone: Milestone = {
      id: this.milestones.length
        ? Math.max(...this.milestones.map(m => m.id)) + 1
        : 1,

      name: this.newMilestone.name,

      description:
        this.newMilestone.description || 'No description',

      plannedDate: this.newMilestone.plannedDate,

      actualDate:
        this.newMilestone.status === 'Completed'
          ? new Date().toISOString().split('T')[0]
          : null,

      status: this.newMilestone.status
    };

    this.milestones.push(milestone);

    this.closeAddMilestone();
  }

  // ============================
  // EDIT MILESTONE
  // ============================

  startEdit(milestone: Milestone): void {

    this.editingMilestoneId = milestone.id;

    this.editForm = {
      name: milestone.name,
      description: milestone.description,
      plannedDate: milestone.plannedDate,
      status: milestone.status
    };
  }

  saveEdit(milestone: Milestone): void {

    milestone.name = this.editForm.name;
    milestone.description = this.editForm.description;
    milestone.plannedDate = this.editForm.plannedDate;
    milestone.status = this.editForm.status;

    if (
      milestone.status === 'Completed' &&
      !milestone.actualDate
    ) {
      milestone.actualDate =
        new Date().toISOString().split('T')[0];
    }

    if (milestone.status !== 'Completed') {
      milestone.actualDate = null;
    }

    this.editingMilestoneId = null;
  }
    // ============================
  // CANCEL EDIT
  // ============================

  cancelEdit(): void {
    this.editingMilestoneId = null;
  }

  // ============================
  // DELETE MILESTONE
  // ============================

  deleteMilestone(id: number): void {

    const confirmed = confirm(
      'Are you sure you want to delete this milestone?'
    );

    if (!confirmed) {
      return;
    }

    this.milestones = this.milestones.filter(
      milestone => milestone.id !== id
    );

    if (this.editingMilestoneId === id) {
      this.editingMilestoneId = null;
    }
  }

}
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
