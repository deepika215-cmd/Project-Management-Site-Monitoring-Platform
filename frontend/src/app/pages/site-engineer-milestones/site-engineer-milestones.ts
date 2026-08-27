import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';
import { SiteProgressService, SiteProgressEntry } from '../../services/site-progress.service';

@Component({
  selector: 'app-site-engineer-milestones',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './site-engineer-milestones.html',
  styleUrl: './site-engineer-milestones.css',
})
export class SiteEngineerMilestones implements OnInit {
  entries: SiteProgressEntry[] = [];

  @ViewChild('photoInput') photoInput!: ElementRef<HTMLInputElement>;
  @ViewChild('videoInput') videoInput!: ElementRef<HTMLInputElement>;

  form = {
    projectName: '',
    date: new Date().toISOString().slice(0, 10),
    progress: 0,
    workCompleted: '',
    workDescription: '',
    engineerName: '',
    issues: '',
    tasks: '',
    nextPlan: '',
    photos: [] as string[],
    videos: [] as string[],
    location: '',
    weather: '',
    category: 'Foundation'
  };

  categories = ['Foundation', 'Structural Work', 'Electrical Work', 'Plumbing Work', 'Finishing Work', 'Inspection Work'];

  constructor(private siteProgressService: SiteProgressService) {}

  get completedCount(): number { return this.entries.filter(e => e.progress >= 100).length; }
  get delayedCount(): number { return this.entries.filter(e => !!e.issues?.trim()).length; }
  get averageProgress(): number { return this.entries.length ? Math.round(this.entries.reduce((s, e) => s + Number(e.progress || 0), 0) / this.entries.length) : 0; }
  get weeklyCount(): number { const cutoff = Date.now() - 7 * 86400000; return this.entries.filter(e => new Date(e.date).getTime() >= cutoff).length; }
  status(progress: number, issues: string): string { if (issues?.trim()) return 'Delayed'; if (progress >= 100) return 'Completed'; if (progress > 0) return 'In Progress'; return 'Planned'; }

  ngOnInit(): void {
    this.siteProgressService.loadEntries().subscribe((entries) => {
      this.entries = entries;
    });
  }

  submitEntry(): void {
    if (!this.form.projectName || !this.form.workCompleted || !this.form.engineerName) {
      return;
    }

    const entry: SiteProgressEntry = {
      id: Date.now(),
      projectName: this.form.projectName,
      date: this.form.date,
      progress: this.form.progress,
      workCompleted: this.form.workCompleted,
      workDescription: this.form.workDescription,
      engineerName: this.form.engineerName,
      issues: this.form.issues,
      tasks: this.form.tasks,
      nextPlan: this.form.nextPlan,
      photos: this.form.photos || [],
      videos: this.form.videos || [],
      location: this.form.location,
      weather: this.form.weather
    };

    this.siteProgressService.addEntry(entry);
    this.entries = this.siteProgressService.getProgressEntries();
    this.form = {
      projectName: '',
      date: new Date().toISOString().slice(0, 10),
      progress: 0,
      workCompleted: '',
      workDescription: '',
      engineerName: '',
      issues: '',
      tasks: '',
      nextPlan: '',
      photos: [] as string[],
      videos: [] as string[],
      location: '',
      weather: '',
      category: 'Foundation'
    };

    if (this.photoInput) {
      this.photoInput.nativeElement.value = '';
    }
    if (this.videoInput) {
      this.videoInput.nativeElement.value = '';
    }
  }

  onPhotoFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;
    this.form.photos = files ? Array.from(files).map(file => file.name) : [];
  }

  onVideoFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;
    this.form.videos = files ? Array.from(files).map(file => file.name) : [];
  }
}
