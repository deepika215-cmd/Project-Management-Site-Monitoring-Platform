import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, forkJoin, of } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class Reports implements OnInit {
  reportTypes = ['Project Progress', 'Resource Utilization', 'Budget', 'Workforce', 'Procurement'];
  reports: any[] = [];
  projects: any[] = [];
  loading = false;
  saving = false;
  actionReportId: number | null = null;
  actionKind: 'preview' | 'pdf' | 'xlsx' | 'delete' | null = null;
  error = '';
  message = '';
  preview: any = null;
  selectedType = 'Project Progress';
  selectedProjectId: number | null = null;
  dateFrom = '';
  dateTo = '';
  form = { title: '', description: '', report_type: 'Project Progress', status: 'Generated' };

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}
  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true; this.error = '';
    forkJoin({ reports: this.api.getReports().pipe(catchError(() => of([]))), projects: this.api.getProjects().pipe(catchError(() => of([]))) }).subscribe({
      next: data => { this.reports = Array.isArray(data.reports) ? data.reports : []; this.projects = Array.isArray(data.projects) ? data.projects : []; this.loading = false; this.cdr.detectChanges(); },
      error: () => { this.loading = false; this.error = 'Unable to load reports.'; this.cdr.detectChanges(); }
    });
  }

  get filteredReports(): any[] {
    return this.reports.filter(report => {
      const typeOk = !this.selectedType || String(report.report_type || '') === this.selectedType;
      const projectValue = report.project_id ?? report.project?.id;
      const projectOk = !this.selectedProjectId || projectValue == null || Number(projectValue) === Number(this.selectedProjectId);
      const created = report.created_at || report.createdAt;
      const fromOk = !this.dateFrom || !created || new Date(created) >= new Date(`${this.dateFrom}T00:00:00`);
      const toOk = !this.dateTo || !created || new Date(created) <= new Date(`${this.dateTo}T23:59:59`);
      return typeOk && projectOk && fromOk && toOk;
    });
  }

  chooseType(type: string): void { this.selectedType = type; this.form.report_type = type; this.preview = null; }

  generate(): void {
    const project = this.projects.find(p => Number(p.id) === Number(this.selectedProjectId));
    const projectName = project?.project_name || project?.name || '';
    const title = this.form.title.trim() || `${this.selectedType}${projectName ? ` - ${projectName}` : ''}`;
    const filterText = [this.dateFrom ? `From ${this.dateFrom}` : '', this.dateTo ? `To ${this.dateTo}` : ''].filter(Boolean).join(', ');
    const description = this.form.description.trim() || [projectName ? `Project: ${projectName}` : '', filterText].filter(Boolean).join(' | ') || null;
    this.saving = true; this.error = ''; this.message = '';
    this.api.createReport({ title, description, report_type: this.selectedType, status: 'Generated' }).subscribe({
      next: report => { this.saving = false; this.message = 'Report generated from the selected report configuration.'; this.cdr.detectChanges(); this.load(); if (report?.id) this.view(report); },
      error: e => { this.saving = false; this.error = e?.error?.detail || 'Unable to generate the report.'; this.cdr.detectChanges(); }
    });
  }

  view(report: any): void {
    this.error = ''; this.message = '';
    this.actionReportId = Number(report.id); this.actionKind = 'preview';
    this.api.previewReport(Number(report.id)).subscribe({
      next: data => { this.preview = data; this.actionReportId = null; this.actionKind = null; this.cdr.detectChanges(); },
      error: e => { this.actionReportId = null; this.actionKind = null; this.error = e?.error?.detail || `Unable to load the report preview (HTTP ${e?.status || 'error'}).`; this.cdr.detectChanges(); }
    });
  }

  export(report: any, format: 'pdf' | 'xlsx'): void {
    this.error = ''; this.message = '';
    this.actionReportId = Number(report.id); this.actionKind = format;
    this.api.exportReport(Number(report.id), format).subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${String(report.title || 'BuildTrack_Report').replace(/[^a-z0-9_-]+/gi, '_')}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        this.actionReportId = null; this.actionKind = null;
        this.message = `${format === 'pdf' ? 'PDF' : 'Excel'} export created.`;
        this.cdr.detectChanges();
      },
      error: e => { this.actionReportId = null; this.actionKind = null; this.error = e?.error?.detail || `Unable to export ${format === 'pdf' ? 'PDF' : 'Excel'} (HTTP ${e?.status || 'error'}).`; this.cdr.detectChanges(); }
    });
  }

  remove(report: any): void {
    if (!confirm(`Delete report ${report.title || ''}?`)) return;
    this.error = ''; this.message = '';
    this.actionReportId = Number(report.id); this.actionKind = 'delete';
    this.api.deleteReport(Number(report.id)).subscribe({
      next: () => { this.actionReportId = null; this.actionKind = null; this.preview = null; this.message = 'Report deleted successfully.'; this.cdr.detectChanges(); this.load(); },
      error: e => { this.actionReportId = null; this.actionKind = null; this.error = e?.error?.detail || `Unable to delete the report (HTTP ${e?.status || 'error'}).`; this.cdr.detectChanges(); }
    });
  }
}
