import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({ selector: 'app-reports', standalone: true, imports: [CommonModule, FormsModule, AppSidebarComponent], templateUrl: './reports.html', styleUrl: './reports.css' })
export class Reports implements OnInit {
  reports: any[] = []; loading = false; saving = false; error = ''; showForm = false; editingId: number | null = null;
  form = { title: '', description: '', report_type: 'Project Progress', status: 'Draft' };
  constructor(private api: Api) {}
  ngOnInit(): void { this.load(); }
  load(): void { this.loading = true; this.api.getReports().subscribe({ next: rows => { this.reports = Array.isArray(rows) ? rows : []; this.loading = false; }, error: e => { this.loading = false; this.error = e?.error?.detail || 'Unable to load reports.'; } }); }
  openCreate(): void { this.editingId = null; this.form = { title: '', description: '', report_type: 'Project Progress', status: 'Draft' }; this.showForm = true; this.error = ''; }
  edit(report: any): void { this.editingId = Number(report.id); this.form = { title: report.title || '', description: report.description || '', report_type: report.report_type || 'Project Progress', status: report.status || 'Draft' }; this.showForm = true; this.error = ''; }
  cancel(): void { this.showForm = false; this.saving = false; }
  save(): void { if (!this.form.title.trim()) { this.error = 'Report title is required.'; return; } this.saving = true; const payload = { ...this.form, title: this.form.title.trim(), description: this.form.description.trim() || null }; const request = this.editingId ? this.api.updateReport(this.editingId, payload) : this.api.createReport(payload); request.subscribe({ next: () => { this.showForm = false; this.saving = false; this.load(); }, error: e => { this.saving = false; this.error = e?.error?.detail || 'Unable to save report.'; } }); }
  remove(report: any): void { if (!confirm(`Delete report ${report.title}?`)) return; this.api.deleteReport(Number(report.id)).subscribe({ next: () => this.load(), error: e => this.error = e?.error?.detail || 'Unable to delete report.' }); }
}
