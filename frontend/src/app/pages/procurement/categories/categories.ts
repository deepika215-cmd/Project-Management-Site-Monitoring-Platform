import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

interface Category {
  id: number;
  name?: string;
  category_name?: string;
  description?: string | null;
  status?: string;
}

@Component({
  selector: 'app-categories',
  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    AppSidebarComponent
  ],

  templateUrl: './categories.html',
  styleUrl: './categories.css'
})
export class Categories implements OnInit {

  // =====================================================
  // CATEGORY DATA
  // =====================================================

  categories: Category[] = [];

  // =====================================================
  // STATES
  // =====================================================

  loading = false;
  saving = false;
  deleting = false;

  error = '';
  success = '';

  showForm = false;

  editingId: number | null = null;

  searchText = '';

  // =====================================================
  // FORM
  // =====================================================

  form = {
    name: '',
    description: '',
    status: 'Active'
  };

  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(
    private api: Api
  ) {}

  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {
    this.loadCategories();
  }

  // =====================================================
  // LOAD CATEGORIES FROM DATABASE
  // =====================================================

  loadCategories(): void {

    this.loading = true;
    this.error = '';

    this.api.getCategories().subscribe({

      next: (rows: any) => {

        this.categories = Array.isArray(rows)
          ? rows
          : [];

        this.loading = false;
      },

      error: (e: any) => {

        console.error(
          'Load categories error:',
          e
        );

        this.loading = false;

        this.categories = [];

        this.error =
          e?.error?.detail ||
          e?.error?.message ||
          'Unable to load categories. Please make sure backend is running.';
      }

    });
  }

  // =====================================================
  // OPEN CREATE FORM
  // =====================================================

  openCreate(): void {

    this.editingId = null;

    this.form = {
      name: '',
      description: '',
      status: 'Active'
    };

    this.showForm = true;

    this.error = '';
    this.success = '';
  }

  // =====================================================
  // EDIT CATEGORY
  // =====================================================

  edit(category: Category): void {

    const id = Number(category?.id);

    if (!id) {

      this.error = 'Invalid category ID.';
      return;
    }

    this.editingId = id;

    this.form = {

      name:
        category.name ??
        category.category_name ??
        '',

      description:
        category.description ??
        '',

      status:
        category.status ??
        'Active'
    };

    this.showForm = true;

    this.error = '';
    this.success = '';
  }

  // =====================================================
  // CANCEL FORM
  // =====================================================

  cancel(): void {

    this.showForm = false;

    this.editingId = null;

    this.saving = false;

    this.form = {
      name: '',
      description: '',
      status: 'Active'
    };

    this.error = '';
  }

  // =====================================================
  // SAVE CATEGORY
  // CREATE / UPDATE
  // =====================================================

  save(): void {

    this.error = '';
    this.success = '';

    const name =
      this.form.name
        .trim();

    const description =
      this.form.description
        .trim();

    // ===================================================
    // VALIDATION
    // ===================================================

    if (!name) {

      this.error =
        'Category name is required.';

      return;
    }

    if (name.length < 2) {

      this.error =
        'Category name must contain at least 2 characters.';

      return;
    }

    if (name.length > 100) {

      this.error =
        'Category name cannot exceed 100 characters.';

      return;
    }

    if (description.length > 500) {

      this.error =
        'Description cannot exceed 500 characters.';

      return;
    }

    if (!this.form.status) {

      this.error =
        'Please select a status.';

      return;
    }

    // ===================================================
    // PAYLOAD
    // ===================================================

    const payload = {

      name: name,

      description:
        description || null,

      status:
        this.form.status
    };

    // Save whether this is update or create
    const wasEditing =
      this.editingId !== null;

    this.saving = true;

    // ===================================================
    // UPDATE
    // ===================================================

    if (wasEditing) {

      this.api.updateCategory(
        this.editingId as number,
        payload
      ).subscribe({

        next: (response: any) => {

          console.log(
            'Category updated:',
            response
          );

          this.saving = false;

          this.showForm = false;

          this.editingId = null;

          this.form = {
            name: '',
            description: '',
            status: 'Active'
          };

          this.success =
            'Category updated successfully.';

          // IMPORTANT:
          // Database se fresh data load
          this.loadCategories();
        },

        error: (e: any) => {

          console.error(
            'Update category error:',
            e
          );

          this.saving = false;

          this.error =
            e?.error?.detail ||
            e?.error?.message ||
            'Unable to update category.';
        }

      });

      return;
    }

    // ===================================================
    // CREATE
    // ===================================================

    this.api.createCategory(
      payload
    ).subscribe({

      next: (response: any) => {

        console.log(
          'Category created:',
          response
        );

        this.saving = false;

        this.showForm = false;

        this.editingId = null;

        this.form = {
          name: '',
          description: '',
          status: 'Active'
        };

        this.success =
          'Category created successfully.';

        // IMPORTANT:
        // Database se fresh data load
        this.loadCategories();
      },

      error: (e: any) => {

        console.error(
          'Create category error:',
          e
        );

        this.saving = false;

        this.error =
          e?.error?.detail ||
          e?.error?.message ||
          'Unable to create category.';
      }

    });
  }

  // =====================================================
  // DELETE CATEGORY
  // =====================================================

  remove(category: Category): void {

    const id =
      Number(category?.id);

    if (!id) {

      this.error =
        'Invalid category ID.';

      return;
    }

    const name =
      this.getCategoryName(category);

    const confirmed =
      confirm(
        `Delete category "${name}"?`
      );

    if (!confirmed) {
      return;
    }

    this.deleting = true;

    this.error = '';
    this.success = '';

    this.api.deleteCategory(
      id
    ).subscribe({

      next: (response: any) => {

        console.log(
          'Category deleted:',
          response
        );

        this.deleting = false;

        this.success =
          'Category deleted successfully.';

        // IMPORTANT:
        // Database se fresh data load
        this.loadCategories();
      },

      error: (e: any) => {

        console.error(
          'Delete category error:',
          e
        );

        this.deleting = false;

        this.error =
          e?.error?.detail ||
          e?.error?.message ||
          'Unable to delete category.';
      }

    });
  }

  // =====================================================
  // SEARCH
  // =====================================================

  get filteredCategories(): Category[] {

    const search =
      this.searchText
        .trim()
        .toLowerCase();

    if (!search) {

      return this.categories;
    }

    return this.categories.filter(
      (category: Category) => {

        const name =
          this.getCategoryName(category)
            .toLowerCase();

        const description =
          this.getDescription(category)
            .toLowerCase();

        const status =
          this.getStatus(category)
            .toLowerCase();

        return (
          name.includes(search) ||
          description.includes(search) ||
          status.includes(search)
        );
      }
    );
  }

  // =====================================================
  // CATEGORY NAME
  // =====================================================

  getCategoryName(
    category: Category
  ): string {

    return (
      category?.name ||
      category?.category_name ||
      `Category #${category?.id || ''}`
    );
  }

  // =====================================================
  // DESCRIPTION
  // =====================================================

  getDescription(
    category: Category
  ): string {

    return (
      category?.description ||
      'No description'
    );
  }

  // =====================================================
  // STATUS
  // =====================================================

  getStatus(
    category: Category
  ): string {

    return (
      category?.status ||
      'Active'
    );
  }

  // =====================================================
  // STATUS CLASS
  // =====================================================

  getStatusClass(
    status: string
  ): string {

    switch (
      (status || '')
        .toLowerCase()
        .trim()
    ) {

      case 'active':
        return 'status-active';

      case 'inactive':
        return 'status-inactive';

      case 'pending':
        return 'status-pending';

      case 'completed':
        return 'status-completed';

      default:
        return 'status-default';
    }
  }

  // =====================================================
  // TOTAL CATEGORIES
  // =====================================================

  get totalCategories(): number {

    return this.categories.length;
  }

  // =====================================================
  // ACTIVE CATEGORIES
  // =====================================================

  get activeCategories(): number {

    return this.categories.filter(
      (category: Category) =>
        this.getStatus(category)
          .toLowerCase() === 'active'
    ).length;
  }

  // =====================================================
  // INACTIVE CATEGORIES
  // =====================================================

  get inactiveCategories(): number {

    return this.categories.filter(
      (category: Category) =>
        this.getStatus(category)
          .toLowerCase() === 'inactive'
    ).length;
  }

  // =====================================================
  // CLEAR SEARCH
  // =====================================================

  clearSearch(): void {

    this.searchText = '';
  }

  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {

    this.success = '';
    this.error = '';

    this.searchText = '';

    this.loadCategories();
  }
}