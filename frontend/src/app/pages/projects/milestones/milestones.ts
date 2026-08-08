import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

interface Milestone {
  id: number;
  name: string;
  description: string;
  plannedDate: string;
  actualDate: string | null;
  status: string;
}

@Component({
  selector: 'app-milestones',
  standalone: true,
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