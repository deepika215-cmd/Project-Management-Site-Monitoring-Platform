import { CommonModule } from '@angular/common';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-site-progress',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './site-progress.html',
  styleUrl: './site-progress.css'
})
export class SiteProgress implements OnInit {
  projects: any[] = [];
  milestones: any[] = [];
  daily: any[] = [];
  weekly: any[] = [];
  delays: any[] = [];
  activities: any[] = [];
  loading = false;
  saving = false;
  message = '';
  error = '';
  tab: 'daily'|'weekly'|'delays'|'activities' = 'daily';
  categories = ['Foundation','Structural Work','Electrical Work','Plumbing Work','Finishing Work','Inspection Work'];
  today = new Date().toISOString().slice(0,10);
  dailyForm: any = {project_id:0,milestone_id:null,report_date:this.today,work_category:'Foundation',activity:'',completion_percentage:0,contractor_name:'',workers_present:0,workers_absent:0,machinery_used:'',materials_used:'',weather:'',safety_observation:'',quality_remarks:'',delay_hours:0,delay_reason:'',comments:''};
  weeklyForm: any = {project_id:0,week_start:this.today,week_end:this.today,work_completed:'',completion_percentage:0,worker_hours:0,major_activities:'',delays:'',safety_incidents:'',overall_status:'In Progress'};
  delayForm: any = {project_id:0,delay_date:this.today,reason:'',duration_hours:1,affected_work:'',impact:''};
  activityForm: any = {project_id:0,activity_type:'Inspection',activity_at:new Date().toISOString().slice(0,16),description:'',responsible_person:''};

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}
  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true;
    this.error = '';
    forkJoin({
      projects: this.api.getProjects().pipe(timeout(9000), catchError(() => of([] as any[]))),
      milestones: this.api.getMilestones().pipe(timeout(9000), catchError(() => of([] as any[]))),
      daily: this.api.getDailyProgress().pipe(timeout(9000), catchError(() => of([] as any[]))),
      weekly: this.api.getWeeklyProgress().pipe(timeout(9000), catchError(() => of([] as any[]))),
      delays: this.api.getDelayRecords().pipe(timeout(9000), catchError(() => of([] as any[]))),
      activities: this.api.getSiteActivityLogs().pipe(timeout(9000), catchError(() => of([] as any[])))
    }).pipe(finalize(() => { this.loading = false; this.cdr.detectChanges(); }))
      .subscribe(r => {
        this.projects = r.projects || [];
        this.milestones = r.milestones || [];
        this.daily = r.daily || [];
        this.weekly = r.weekly || [];
        this.delays = r.delays || [];
        this.activities = r.activities || [];
        this.setDefaultProject();
      });
  }

  projectName(id: number): string { return this.projects.find(p => Number(p.id) === Number(id))?.project_name || `Project #${id}`; }
  filteredMilestones(): any[] { return this.milestones.filter(m => !this.dailyForm.project_id || Number(m.project_id) === Number(this.dailyForm.project_id)); }

  submitDaily(): void {
    if (!this.dailyForm.project_id || !this.dailyForm.activity.trim()) { this.error = 'Project and activity are required.'; return; }
    this.save(this.api.createDailyProgress({...this.dailyForm, milestone_id: this.dailyForm.milestone_id || null}), 'Daily progress report saved.', () => {
      this.dailyForm = {...this.dailyForm, activity:'', completion_percentage:0, contractor_name:'', workers_present:0, workers_absent:0, machinery_used:'', materials_used:'', safety_observation:'', quality_remarks:'', delay_hours:0, delay_reason:'', comments:''};
    });
  }

  submitWeekly(): void {
    if (!this.weeklyForm.project_id || !this.weeklyForm.work_completed.trim()) { this.error = 'Project and work completed are required.'; return; }
    this.save(this.api.createWeeklyProgress(this.weeklyForm), 'Weekly progress report saved.');
  }

  submitDelay(): void {
    if (!this.delayForm.project_id || !this.delayForm.reason.trim()) { this.error = 'Project and delay reason are required.'; return; }
    this.save(this.api.createDelayRecord(this.delayForm), 'Delay record saved.', () => {
      this.delayForm = {...this.delayForm, reason:'', duration_hours:1, affected_work:'', impact:''};
    });
  }

  submitActivity(): void {
    if (!this.activityForm.project_id || !this.activityForm.description.trim()) { this.error = 'Project and description are required.'; return; }
    const when = this.activityForm.activity_at ? new Date(this.activityForm.activity_at) : new Date();
    const payload = {
      project_id: Number(this.activityForm.project_id),
      activity_date: when.toISOString().slice(0, 10),
      activity_time: when.toTimeString().slice(0, 5),
      activity_type: this.activityForm.activity_type,
      description: this.activityForm.description.trim(),
      responsible_person: this.activityForm.responsible_person || ''
    };
    this.save(this.api.createSiteActivityLog(payload), 'Site activity logged.', () => {
      this.activityForm = {...this.activityForm, description:'', responsible_person:''};
    });
  }

  removeDaily(id: number): void { if (confirm('Delete this daily report?')) this.remove(this.api.deleteDailyProgress(id), () => this.daily = this.daily.filter(x => x.id !== id)); }
  removeWeekly(id: number): void { if (confirm('Delete this weekly report?')) this.remove(this.api.deleteWeeklyProgress(id), () => this.weekly = this.weekly.filter(x => x.id !== id)); }
  removeDelay(id: number): void { if (confirm('Delete this delay record?')) this.remove(this.api.deleteDelayRecord(id), () => this.delays = this.delays.filter(x => x.id !== id)); }
  removeActivity(id: number): void { if (confirm('Delete this site activity log?')) this.remove(this.api.deleteSiteActivityLog(id), () => this.activities = this.activities.filter(x => x.id !== id)); }

  completion(): number { return this.daily.length ? Math.round(this.daily.reduce((s,r) => s + Number(r.completion_percentage || 0), 0) / this.daily.length) : 0; }
  present(): number { return this.daily.reduce((s,r) => s + Number(r.workers_present || 0), 0); }

  private save(request: any, successMessage: string, reset?: () => void): void {
    this.saving = true;
    this.error = '';
    this.message = '';
    request.pipe(timeout(10000), finalize(() => { this.saving = false; this.cdr.detectChanges(); }))
      .subscribe({ next: () => { this.message = successMessage; reset?.(); this.load(); }, error: (e: any) => this.error = this.detail(e, 'Unable to save record.') });
  }

  private remove(request: any, updateLocal: () => void): void {
    this.error = '';
    request.pipe(timeout(10000)).subscribe({ next: () => { updateLocal(); this.message = 'Record deleted.'; }, error: (e: any) => this.error = this.detail(e, 'Unable to delete record.') });
  }

  private setDefaultProject(): void {
    const first = Number(this.projects[0]?.id || 0);
    if (!this.dailyForm.project_id) this.dailyForm.project_id = first;
    if (!this.weeklyForm.project_id) this.weeklyForm.project_id = first;
    if (!this.delayForm.project_id) this.delayForm.project_id = first;
    if (!this.activityForm.project_id) this.activityForm.project_id = first;
  }

  private detail(e: any, fallback: string): string {
    const d = e?.error?.detail ?? e?.error?.message ?? e?.message;
    return Array.isArray(d) ? d.map((x: any) => x?.msg || String(x)).join(', ') : d || fallback;
  }
}
