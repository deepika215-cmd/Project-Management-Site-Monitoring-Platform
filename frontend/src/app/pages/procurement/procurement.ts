// import { CommonModule } from '@angular/common';
// import { Component, OnInit } from '@angular/core';
// import { FormsModule } from '@angular/forms';
// import { Api } from '../../services/api';
// import { AppSidebarComponent } from '../../shared/app-sidebar.component';

// @Component({ selector: 'app-procurement', standalone: true, imports: [CommonModule, FormsModule, AppSidebarComponent], templateUrl: './procurement.html', styleUrl: './procurement.css' })
// export class Procurement implements OnInit {
//   items: any[] = []; projects: any[] = []; loading = false; saving = false; error = ''; showForm = false; editingId: number | null = null;
//   form = { item_name: '', quantity: 1, supplier: '', status: 'Pending', project_id: 0 };
//   constructor(private api: Api) {}
//   ngOnInit(): void { this.load(); }
//   load(): void {
//     this.loading = true; this.error = '';
//     this.api.getProcurements().subscribe({ next: rows => { this.items = Array.isArray(rows) ? rows : []; this.loading = false; }, error: e => { this.loading = false; this.error = e?.error?.detail || 'Unable to load procurement records.'; } });
//     this.api.getProjects().subscribe({ next: rows => this.projects = Array.isArray(rows) ? rows : [], error: () => this.projects = [] });
//   }
//   openCreate(): void { this.editingId = null; this.form = { item_name: '', quantity: 1, supplier: '', status: 'Pending', project_id: Number(this.projects[0]?.id || 0) }; this.showForm = true; this.error = ''; }
//   edit(item: any): void { this.editingId = Number(item.id); this.form = { item_name: item.item_name || '', quantity: Number(item.quantity) || 1, supplier: item.supplier || '', status: item.status || 'Pending', project_id: Number(item.project_id) || 0 }; this.showForm = true; this.error = ''; }
//   cancel(): void { this.showForm = false; this.saving = false; }
//   save(): void {
//     if (!this.form.item_name.trim() || this.form.quantity < 1 || !this.form.supplier.trim() || !this.form.project_id) { this.error = 'Item, quantity, supplier and project are required.'; return; }
//     this.saving = true;
//     const payload = { ...this.form, item_name: this.form.item_name.trim(), supplier: this.form.supplier.trim(), quantity: Number(this.form.quantity), project_id: Number(this.form.project_id) };
//     const request = this.editingId ? this.api.updateProcurement(this.editingId, payload) : this.api.createProcurement(payload);
//     request.subscribe({ next: () => { this.showForm = false; this.saving = false; this.load(); }, error: e => { this.saving = false; this.error = e?.error?.detail || 'Unable to save procurement record.'; } });
//   }
//   remove(item: any): void { if (!confirm(`Delete procurement for ${item.item_name}?`)) return; this.api.deleteProcurement(Number(item.id)).subscribe({ next: () => this.load(), error: e => this.error = e?.error?.detail || 'Unable to delete procurement record.' }); }
// }


import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-procurement',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AppSidebarComponent
  ],
  templateUrl: './procurement.html',
  styleUrl: './procurement.css'
})
export class Procurement implements OnInit {

  items: any[] = [];

  projects: any[] = [];

  loading = false;

  saving = false;

  error = '';

  showForm = false;

  editingId: number | null = null;


  form = {
    item_name: '',
    quantity: 1,
    supplier: '',
    status: 'Pending',
    project_id: 0
  };


  constructor(private api: Api) {}


  ngOnInit(): void {
    this.load();
  }


  // ================================
  // LOAD PROCUREMENT + PROJECTS
  // ================================

  load(): void {

    this.loading = true;

    this.error = '';


    this.api.getProcurements().subscribe({

      next: (rows: any) => {

        this.items = Array.isArray(rows)
          ? rows
          : [];

        this.loading = false;

      },

      error: (e: any) => {

        this.loading = false;

        this.error =
          e?.error?.detail ||
          'Unable to load procurement records.';

      }

    });


    this.api.getProjects().subscribe({

      next: (rows: any) => {

        this.projects = Array.isArray(rows)
          ? rows
          : [];

      },

      error: () => {

        this.projects = [];

      }

    });

  }


  // ================================
  // OPEN CREATE FORM
  // ================================

  openCreate(): void {

    this.editingId = null;

    this.form = {

      item_name: '',

      quantity: 1,

      supplier: '',

      status: 'Pending',

      project_id: Number(
        this.projects[0]?.id || 0
      )

    };

    this.showForm = true;

    this.error = '';

  }


  // ================================
  // EDIT
  // ================================

  edit(item: any): void {

    this.editingId = Number(item.id);

    this.form = {

      item_name: item.item_name || '',

      quantity:
        Number(item.quantity) || 1,

      supplier:
        item.supplier || '',

      status:
        item.status || 'Pending',

      project_id:
        Number(item.project_id) || 0

    };

    this.showForm = true;

    this.error = '';

    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });

  }


  // ================================
  // CANCEL
  // ================================

  cancel(): void {

    this.showForm = false;

    this.saving = false;

    this.editingId = null;

    this.error = '';

  }


  // ================================
  // SAVE
  // ================================

  save(): void {

    this.error = '';


    // ITEM VALIDATION

    if (!this.form.item_name.trim()) {

      this.error =
        'Please enter the item name.';

      return;

    }


    // QUANTITY VALIDATION

    if (
      !this.form.quantity ||
      Number(this.form.quantity) < 1
    ) {

      this.error =
        'Quantity must be at least 1.';

      return;

    }


    // SUPPLIER VALIDATION

    if (!this.form.supplier.trim()) {

      this.error =
        'Please enter the supplier name.';

      return;

    }


    // PROJECT VALIDATION

    if (!this.form.project_id) {

      this.error =
        'Please select a project.';

      return;

    }


    this.saving = true;


    const payload = {

      item_name:
        this.form.item_name.trim(),

      quantity:
        Number(this.form.quantity),

      supplier:
        this.form.supplier.trim(),

      status:
        this.form.status,

      project_id:
        Number(this.form.project_id)

    };


    const request = this.editingId

      ? this.api.updateProcurement(
          this.editingId,
          payload
        )

      : this.api.createProcurement(
          payload
        );


    request.subscribe({

      next: () => {

        this.showForm = false;

        this.saving = false;

        this.editingId = null;

        this.load();

      },

      error: (e: any) => {

        this.saving = false;

        this.error =
          e?.error?.detail ||
          'Unable to save procurement record.';

      }

    });

  }


  // ================================
  // DELETE
  // ================================

  remove(item: any): void {

    const confirmed = confirm(
      `Delete procurement for "${item.item_name}"?`
    );


    if (!confirmed) {
      return;
    }


    this.api
      .deleteProcurement(Number(item.id))
      .subscribe({

        next: () => {

          this.load();

        },

        error: (e: any) => {

          this.error =
            e?.error?.detail ||
            'Unable to delete procurement record.';

        }

      });

  }


  // ================================
  // PROJECT NAME
  // ================================

  getProjectName(projectId: number): string {

    const project = this.projects.find(
      p => Number(p.id) === Number(projectId)
    );


    return project?.project_name ||
      `Project #${projectId}`;

  }


  // ================================
  // STATUS CLASS
  // ================================

  getStatusClass(status: string): string {

    switch (
      String(status || '')
        .toLowerCase()
    ) {

      case 'pending':
        return 'pending';

      case 'ordered':
        return 'ordered';

      case 'received':
        return 'received';

      case 'completed':
        return 'completed';

      default:
        return 'pending';

    }

  }


  // ================================
  // INITIAL
  // ================================

  getInitial(name: string): string {

    if (!name) {
      return 'P';
    }


    return name
      .trim()
      .charAt(0)
      .toUpperCase();

  }


  // ================================
  // USAGE %
  // ================================

  getUsagePercent(item: any): number {

    const quantity =
      Number(item.quantity) || 0;

    const used =
      Number(item.used) || 0;


    if (quantity <= 0) {
      return 0;
    }


    const percentage =
      (used / quantity) * 100;


    return Math.min(
      100,
      Math.max(
        0,
        Math.round(percentage)
      )
    );

  }


  // ================================
  // PENDING COUNT
  // ================================

  get pendingCount(): number {

    return this.items.filter(
      item =>
        String(item.status)
          .toLowerCase() === 'pending'
    ).length;

  }


  // ================================
  // ORDERED COUNT
  // ================================

  get orderedCount(): number {

    return this.items.filter(
      item =>
        String(item.status)
          .toLowerCase() === 'ordered'
    ).length;

  }


  // ================================
  // RECEIVED COUNT
  // ================================

  get receivedCount(): number {

    return this.items.filter(
      item =>
        String(item.status)
          .toLowerCase() === 'received'
    ).length;

  }


  // ================================
  // COMPLETED COUNT
  // ================================

  get completedCount(): number {

    return this.items.filter(
      item =>
        String(item.status)
          .toLowerCase() === 'completed'
    ).length;

  }

}