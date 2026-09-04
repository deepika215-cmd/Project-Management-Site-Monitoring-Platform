import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface BudgetItem {
  id: number;
  category: string;
  description: string;
  project: string;
  budget: number;
  spent: number;
  status: 'On Track' | 'Warning' | 'Critical';
}

@Component({
  selector: 'app-budget',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './budget.html',
  styleUrl: './budget.css'
})
export class Budget {
    Number = Number;

  // =====================================================
  // BUDGET DATA
  // =====================================================

  budgets: BudgetItem[] = [
    {
      id: 1,
      category: 'Materials',
      description: 'Cement, Steel and Bricks',
      project: 'Residential Building',
      budget: 500000,
      spent: 325000,
      status: 'On Track'
    },
    {
      id: 2,
      category: 'Equipment',
      description: 'Crane and Excavator',
      project: 'Highway Project',
      budget: 350000,
      spent: 280000,
      status: 'Warning'
    },
    {
      id: 3,
      category: 'Workforce',
      description: 'Labour and Site Engineers',
      project: 'Residential Building',
      budget: 450000,
      spent: 300000,
      status: 'On Track'
    },
    {
      id: 4,
      category: 'Transportation',
      description: 'Material Transportation',
      project: 'Highway Project',
      budget: 250000,
      spent: 230000,
      status: 'Critical'
    }
  ];

  // =====================================================
  // SEARCH / FILTER
  // =====================================================

  searchText = '';

  selectedProject = 'All Projects';

  selectedStatus = 'All Status';

  // =====================================================
  // MODAL
  // =====================================================

  showModal = false;

  isEditing = false;

  editingId: number | null = null;

  // =====================================================
  // FORM
  // =====================================================

  form = {
    category: '',
    description: '',
    project: '',
    budget: 0,
    spent: 0
  };

  // =====================================================
  // GET TOTAL BUDGET
  // =====================================================

  get totalBudget(): number {
    return this.budgets.reduce(
      (total, item) => total + Number(item.budget),
      0
    );
  }

  // =====================================================
  // GET TOTAL SPENT
  // =====================================================

  get totalSpent(): number {
    return this.budgets.reduce(
      (total, item) => total + Number(item.spent),
      0
    );
  }

  // =====================================================
  // GET REMAINING
  // =====================================================

  get remainingBudget(): number {
    return this.totalBudget - this.totalSpent;
  }

  // =====================================================
  // GET UTILIZATION
  // =====================================================

  get utilization(): number {

    if (this.totalBudget === 0) {
      return 0;
    }

    return Math.round(
      (this.totalSpent / this.totalBudget) * 100
    );
  }

  // =====================================================
  // FILTERED BUDGETS
  // =====================================================

  get filteredBudgets(): BudgetItem[] {

    const search = this.searchText
      .trim()
      .toLowerCase();

    return this.budgets.filter(item => {

      const matchesSearch =
        !search ||
        item.category.toLowerCase().includes(search) ||
        item.description.toLowerCase().includes(search) ||
        item.project.toLowerCase().includes(search);

      const matchesProject =
        this.selectedProject === 'All Projects' ||
        item.project === this.selectedProject;

      const matchesStatus =
        this.selectedStatus === 'All Status' ||
        item.status === this.selectedStatus;

      return (
        matchesSearch &&
        matchesProject &&
        matchesStatus
      );
    });
  }

  // =====================================================
  // OPEN ADD MODAL
  // =====================================================

  openAddModal(): void {

    this.isEditing = false;

    this.editingId = null;

    this.form = {
      category: '',
      description: '',
      project: '',
      budget: 0,
      spent: 0
    };

    this.showModal = true;
  }

  // =====================================================
  // OPEN EDIT MODAL
  // =====================================================

  openEditModal(item: BudgetItem): void {

    this.isEditing = true;

    this.editingId = item.id;

    this.form = {
      category: item.category,
      description: item.description,
      project: item.project,
      budget: item.budget,
      spent: item.spent
    };

    this.showModal = true;
  }

  // =====================================================
  // CLOSE MODAL
  // =====================================================

  closeModal(): void {

    this.showModal = false;

    this.isEditing = false;

    this.editingId = null;
  }

  // =====================================================
  // SAVE BUDGET
  // =====================================================

  saveBudget(): void {

    if (
      !this.form.category ||
      !this.form.description ||
      !this.form.project ||
      this.form.budget <= 0
    ) {
      alert('Please fill all required fields.');
      return;
    }

    if (this.form.spent < 0) {
      alert('Spent amount cannot be negative.');
      return;
    }

    if (this.form.spent > this.form.budget) {
      alert('Spent amount cannot be greater than budget.');
      return;
    }

    const status = this.calculateStatus(
      this.form.budget,
      this.form.spent
    );

    // ===================================================
    // EDIT
    // ===================================================

    if (this.isEditing && this.editingId !== null) {

      const index = this.budgets.findIndex(
        item => item.id === this.editingId
      );

      if (index !== -1) {

        this.budgets[index] = {
          id: this.editingId,
          category: this.form.category,
          description: this.form.description,
          project: this.form.project,
          budget: Number(this.form.budget),
          spent: Number(this.form.spent),
          status
        };
      }

    }

    // ===================================================
    // ADD
    // ===================================================

    else {

      const newId =
        this.budgets.length > 0
          ? Math.max(...this.budgets.map(item => item.id)) + 1
          : 1;

      this.budgets.push({
        id: newId,
        category: this.form.category,
        description: this.form.description,
        project: this.form.project,
        budget: Number(this.form.budget),
        spent: Number(this.form.spent),
        status
      });
    }

    this.closeModal();
  }

  // =====================================================
  // CALCULATE STATUS
  // =====================================================

  calculateStatus(
    budget: number,
    spent: number
  ): 'On Track' | 'Warning' | 'Critical' {

    if (budget <= 0) {
      return 'Critical';
    }

    const percentage =
      (spent / budget) * 100;

    if (percentage >= 90) {
      return 'Critical';
    }

    if (percentage >= 75) {
      return 'Warning';
    }

    return 'On Track';
  }

  // =====================================================
  // DELETE
  // =====================================================

  deleteBudget(id: number): void {

    const item = this.budgets.find(
      budget => budget.id === id
    );

    if (!item) {
      return;
    }

    const confirmed = confirm(
      `Delete budget for "${item.category}"?`
    );

    if (!confirmed) {
      return;
    }

    this.budgets = this.budgets.filter(
      budget => budget.id !== id
    );
  }

  // =====================================================
  // CLEAR FILTERS
  // =====================================================

  clearFilters(): void {

    this.searchText = '';

    this.selectedProject = 'All Projects';

    this.selectedStatus = 'All Status';
  }

  // =====================================================
  // PROGRESS
  // =====================================================

  getProgress(item: BudgetItem): number {

    if (item.budget <= 0) {
      return 0;
    }

    return Math.min(
      100,
      Math.round(
        (item.spent / item.budget) * 100
      )
    );
  }

  // =====================================================
  // REMAINING FOR ITEM
  // =====================================================

  getRemaining(item: BudgetItem): number {

    return item.budget - item.spent;
  }

  // =====================================================
  // FORMAT CURRENCY
  // =====================================================

  formatCurrency(value: number): string {

    return new Intl.NumberFormat(
      'en-IN',
      {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }
    ).format(value);
  }
}