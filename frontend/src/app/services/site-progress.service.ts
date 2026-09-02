import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

export interface SiteProgressEntry {
  id: number; projectName: string; date: string; progress: number; workCompleted: string;
  workDescription: string; engineerName: string; issues: string; tasks: string; nextPlan: string;
  photos: string[]; videos: string[]; location?: string; weather?: string;
}

@Injectable({ providedIn: 'root' })
export class SiteProgressService {
  private readonly apiUrl = 'http://localhost:8000/site-progress';
  private readonly storageKey = 'buildtrack-site-progress';
  private entries: SiteProgressEntry[] = [];

  constructor(private http: HttpClient) {}

  addEntry(entry: SiteProgressEntry): void {
    this.entries = [entry, ...this.entries];
    this.saveLocal();
    this.http.post(this.apiUrl + '/', this.toApiPayload(entry)).subscribe({ error: () => void 0 });
  }

  loadEntries(): Observable<SiteProgressEntry[]> {
    return this.http.get<any[]>(this.apiUrl + '/').pipe(
      map(response => (response || []).map(item => this.fromApiPayload(item))),
      tap(entries => { this.entries = entries; this.saveLocal(); }),
      catchError(() => {
        this.entries = this.readLocal();
        return of(this.entries);
      })
    );
  }

  getProgressEntries(): SiteProgressEntry[] { return this.entries; }

  private saveLocal(): void {
    try { localStorage.setItem(this.storageKey, JSON.stringify(this.entries)); } catch { /* storage unavailable */ }
  }

  private readLocal(): SiteProgressEntry[] {
    try { return JSON.parse(localStorage.getItem(this.storageKey) || '[]') as SiteProgressEntry[]; } catch { return []; }
  }

  private toApiPayload(entry: SiteProgressEntry): any {
    return { project_name: entry.projectName, progress_date: entry.date, progress_percentage: entry.progress,
      work_completed: entry.workCompleted, work_description: entry.workDescription, engineer_name: entry.engineerName,
      issues: entry.issues, today_tasks: entry.tasks, next_day_plan: entry.nextPlan, photos: entry.photos,
      videos: entry.videos, location: entry.location, weather: entry.weather };
  }

  private fromApiPayload(entry: any): SiteProgressEntry {
    const files = (value: any): string[] => Array.isArray(value) ? value.map(String).filter(Boolean) : typeof value === 'string' ? value.split(',').map(v => v.trim()).filter(Boolean) : [];
    return { id: Number(entry.id || Date.now()), projectName: entry.project_name || '', date: entry.progress_date || '',
      progress: Number(entry.progress_percentage || 0), workCompleted: entry.work_completed || '', workDescription: entry.work_description || '',
      engineerName: entry.engineer_name || '', issues: entry.issues || '', tasks: entry.today_tasks || '', nextPlan: entry.next_day_plan || '',
      photos: files(entry.photos), videos: files(entry.videos), location: entry.location || '', weather: entry.weather || '' };
  }
}
