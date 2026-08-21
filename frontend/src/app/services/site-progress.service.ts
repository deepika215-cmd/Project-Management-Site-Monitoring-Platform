import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface SiteProgressEntry {
  id: number;
  projectName: string;
  date: string;
  progress: number;
  workCompleted: string;
  workDescription: string;
  engineerName: string;
  issues: string;
  tasks: string;
  nextPlan: string;
  photos: string[];
  videos: string[];
  location?: string;
  weather?: string;
}

@Injectable({
  providedIn: 'root'
})
export class SiteProgressService {
  private readonly apiUrl = 'http://localhost:8000/site-progress';
  private entries: SiteProgressEntry[] = [];

  constructor(private http: HttpClient) {}

  addEntry(entry: SiteProgressEntry): void {
    this.entries = [entry, ...this.entries];
    this.http.post(this.apiUrl + '/', this.toApiPayload(entry)).subscribe();
  }

  loadEntries(): Observable<SiteProgressEntry[]> {
    return this.http.get<any[]>(this.apiUrl + '/').pipe(
      map((response) => {
        this.entries = response.map(item => this.fromApiPayload(item));
        return this.entries;
      })
    );
  }

  getProgressEntries(): SiteProgressEntry[] {
    return this.entries;
  }

  private toApiPayload(entry: SiteProgressEntry): any {
    return {
      project_name: entry.projectName,
      progress_date: entry.date,
      progress_percentage: entry.progress,
      work_completed: entry.workCompleted,
      work_description: entry.workDescription,
      engineer_name: entry.engineerName,
      issues: entry.issues,
      today_tasks: entry.tasks,
      next_day_plan: entry.nextPlan,
      photos: entry.photos,
      videos: entry.videos,
      location: entry.location,
      weather: entry.weather
    };
  }

  private fromApiPayload(entry: any): SiteProgressEntry {
    const normalizeFiles = (value: any): string[] => {
      if (Array.isArray(value)) {
        return value.map((item: any) => String(item).trim()).filter(Boolean);
      }
      if (typeof value === 'string') {
        return value.split(',').map((item: string) => item.trim()).filter(Boolean);
      }
      return [];
    };

    return {
      id: entry.id,
      projectName: entry.project_name,
      date: entry.progress_date,
      progress: entry.progress_percentage,
      workCompleted: entry.work_completed,
      workDescription: entry.work_description,
      engineerName: entry.engineer_name,
      issues: entry.issues,
      tasks: entry.today_tasks,
      nextPlan: entry.next_day_plan,
      photos: normalizeFiles(entry.photos),
      videos: normalizeFiles(entry.videos),
      location: entry.location,
      weather: entry.weather
    };
  }
}
