import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({ selector: 'app-procurement', standalone: true, imports: [CommonModule, FormsModule, AppSidebarComponent], templateUrl: './procurement.html', styleUrl: './procurement.css' })
export class Procurement implements OnInit {
  items: any[] = []; projects: any[] = []; loading = false; saving = false; error = ''; showForm = false; editingId: number | null = null;
  form = { item_name: '', quantity: 1, supplier: '', status: 'Pending', project_id: 0 };
  constructor(private api: Api) {}
  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true; this.error = '';
    this.api.getProcurements().subscribe({ next: rows => { this.items = Array.isArray(rows) ? rows : []; this.loading = false; }, error: e => { this.loading = false; this.error = e?.error?.detail || 'Unable to load procurement records.'; } });
    this.api.getProjects().subscribe({ next: rows => this.projects = Array.isArray(rows) ? rows : [], error: () => this.projects = [] });
  }
  openCreate(): void { this.editingId = null; this.form = { item_name: '', quantity: 1, supplier: '', status: 'Pending', project_id: Number(this.projects[0]?.id || 0) }; this.showForm = true; this.error = ''; }
  edit(item: any): void { this.editingId = Number(item.id); this.form = { item_name: item.item_name || '', quantity: Number(item.quantity) || 1, supplier: item.supplier || '', status: item.status || 'Pending', project_id: Number(item.project_id) || 0 }; this.showForm = true; this.error = ''; }
  cancel(): void { this.showForm = false; this.saving = false; }
  save(): void {
    if (!this.form.item_name.trim() || this.form.quantity < 1 || !this.form.supplier.trim() || !this.form.project_id) { this.error = 'Item, quantity, supplier and project are required.'; return; }
    this.saving = true;
    const payload = { ...this.form, item_name: this.form.item_name.trim(), supplier: this.form.supplier.trim(), quantity: Number(this.form.quantity), project_id: Number(this.form.project_id) };
    const request = this.editingId ? this.api.updateProcurement(this.editingId, payload) : this.api.createProcurement(payload);
    request.subscribe({ next: () => { this.showForm = false; this.saving = false; this.load(); }, error: e => { this.saving = false; this.error = e?.error?.detail || 'Unable to save procurement record.'; } });
  }
  remove(item: any): void { if (!confirm(`Delete procurement for ${item.item_name}?`)) return; this.api.deleteProcurement(Number(item.id)).subscribe({ next: () => this.load(), error: e => this.error = e?.error?.detail || 'Unable to delete procurement record.' }); }
}
