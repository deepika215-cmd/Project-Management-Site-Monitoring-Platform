import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({ selector: 'app-analytics', standalone: true, imports: [CommonModule, AppSidebarComponent], templateUrl: './analytics.html', styleUrl: './analytics.css' })
export class Analytics implements OnInit {
  loading = true; error = ''; summary: any = {}; projectProgress: any[] = []; resourceUtilization: any[] = []; inventoryStatus: any[] = []; procurementStatus: any[] = []; workerAttendance: any[] = []; reportSummary: any[] = [];
  constructor(private api: Api) {}
  ngOnInit(): void {
    forkJoin({ summary: this.api.getAnalytics(), projectProgress: this.api.getProjectProgress(), resourceUtilization: this.api.getResourceUtilizationAnalytics(), inventoryStatus: this.api.getInventoryStatus(), procurementStatus: this.api.getProcurementStatus(), workerAttendance: this.api.getWorkerAttendance(), reportSummary: this.api.getReportSummary() }).subscribe({
      next: data => { this.summary = data.summary || {}; this.projectProgress = Array.isArray(data.projectProgress) ? data.projectProgress : []; this.resourceUtilization = Array.isArray(data.resourceUtilization) ? data.resourceUtilization : []; this.inventoryStatus = Array.isArray(data.inventoryStatus) ? data.inventoryStatus : []; this.procurementStatus = Array.isArray(data.procurementStatus) ? data.procurementStatus : []; this.workerAttendance = Array.isArray(data.workerAttendance) ? data.workerAttendance : []; this.reportSummary = Array.isArray(data.reportSummary) ? data.reportSummary : []; this.loading = false; },
      error: e => { this.loading = false; this.error = e?.error?.detail || 'Unable to load analytics from the backend.'; }
    });
  }
  pct(value: any): number { return Math.max(0, Math.min(100, Number(value) || 0)); }
}
