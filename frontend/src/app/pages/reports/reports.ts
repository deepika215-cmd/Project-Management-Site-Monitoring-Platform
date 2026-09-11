import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
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

  constructor(private api: Api, private cdr: ChangeDetectorRef, private router: Router) {}
  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true;
    this.error = '';
    this.message = '';

    forkJoin({
      reports: this.api.getReports().pipe(timeout({ first: 10000 }), catchError(() => of([]))),
      projects: this.api.getProjects().pipe(timeout({ first: 10000 }), catchError(() => of([])))
    }).pipe(
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: data => {
        this.reports = this.toArray(data.reports).map(r => this.normalizeReport(r));
        this.projects = this.toArray(data.projects);
        if (this.selectedProjectId && !this.projects.some(p => Number(p.id) === Number(this.selectedProjectId))) {
          this.selectedProjectId = null;
        }
      },
      error: () => {
        this.reports = [];
        this.projects = [];
        this.error = 'Unable to load reports. Check that the backend is running.';
      }
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

    this.saving = true;
    this.error = '';
    this.message = '';

    this.api.createReport({
      title,
      description,
      report_type: this.selectedType,
      status: 'Generated',
      project_id: this.selectedProjectId
    }).pipe(
      timeout({ first: 10000 }),
      finalize(() => {
        this.saving = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: report => {
        const normalized = this.normalizeReport(report);
        this.message = 'Report generated from the selected report configuration.';
        this.reports = [normalized, ...this.reports.filter(r => Number(r.id) !== Number(normalized.id))];
        if (normalized?.id) {
          this.view(normalized);
        }
      },
      error: e => {
        this.error = this.errorText(e, 'Unable to generate the report.');
      }
    });
  }

  view(report: any): void {
    this.error = '';
    this.message = '';
    this.actionReportId = Number(report.id);
    this.actionKind = 'preview';

    this.api.previewReport(Number(report.id)).pipe(
      timeout({ first: 12000 }),
      finalize(() => {
        this.actionReportId = null;
        this.actionKind = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: data => {
        this.preview = {
          ...data,
          project_id: data?.project_id ?? report?.project_id ?? this.selectedProjectId,
          project_link: data?.project_link || this.projectLink(data?.project_id ?? report?.project_id ?? this.selectedProjectId)
        };
      },
      error: e => {
        this.error = this.errorText(e, `Unable to load the report preview.`);
      }
    });
  }

  openProjectFromReport(report: any): void {
    const projectId = report?.project_id ?? report?.projectId ?? report?.project?.id ?? this.selectedProjectId;
    if (!projectId) {
      this.error = 'Select a project or generate a project-specific report first.';
      return;
    }
    this.router.navigate(['/projects/project-details', Number(projectId)]);
  }

  projectLink(projectId: any): string | null {
    return projectId ? `/projects/project-details/${Number(projectId)}` : null;
  }

  export(report: any, format: 'pdf' | 'xlsx'): void {
    this.error = '';
    this.message = '';
    this.actionReportId = Number(report.id);
    this.actionKind = format;

    this.api.exportReport(Number(report.id), format).pipe(
      timeout({ first: 15000 }),
      finalize(() => {
        this.actionReportId = null;
        this.actionKind = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${String(report.title || 'BuildTrack_Report').replace(/[^a-z0-9_-]+/gi, '_')}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        this.message = `${format === 'pdf' ? 'PDF' : 'Excel'} export created.`;
      },
      error: e => {
        this.error = this.errorText(e, `Unable to export ${format === 'pdf' ? 'PDF' : 'Excel'}.`);
      }
    });
  }

  remove(report: any): void {
    if (!confirm(`Delete report ${report.title || ''}?`)) return;

    this.error = '';
    this.message = '';
    this.actionReportId = Number(report.id);
    this.actionKind = 'delete';

    this.api.deleteReport(Number(report.id)).pipe(
      timeout({ first: 10000 }),
      finalize(() => {
        this.actionReportId = null;
        this.actionKind = null;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        this.preview = null;
        this.reports = this.reports.filter(r => Number(r.id) !== Number(report.id));
        this.message = 'Report deleted successfully.';
      },
      error: e => {
        this.error = this.errorText(e, `Unable to delete the report.`);
      }
    });
  }

  private toArray(value: any): any[] {
    if (Array.isArray(value)) return value;
    if (Array.isArray(value?.data)) return value.data;
    if (Array.isArray(value?.items)) return value.items;
    if (Array.isArray(value?.reports)) return value.reports;
    if (Array.isArray(value?.projects)) return value.projects;
    return [];
  }

  private normalizeReport(report: any): any {
    const projectId = report?.project_id ?? report?.projectId ?? report?.project?.id ?? null;
    return {
      ...report,
      project_id: projectId,
      projectId,
      title: report?.title || 'Untitled report',
      report_type: report?.report_type || report?.reportType || report?.type || 'Project Progress',
      status: report?.status || 'Generated'
    };
  }

  private errorText(error: any, fallback: string): string {
    const detail = error?.error?.detail;
    if (typeof detail === 'string' && detail.trim()) return detail;
    if (Array.isArray(detail)) return detail.map((x: any) => x?.msg || x?.message || JSON.stringify(x)).join(' | ');
    if (error?.status === 0) return 'Backend is not responding. Start FastAPI on http://localhost:8000 and refresh.';
    return fallback;
  }
}

