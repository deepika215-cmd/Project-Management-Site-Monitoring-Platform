import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { SiteProgressService, SiteProgressEntry } from '../../services/site-progress.service';

@Component({
  selector: 'app-site-engineer-milestones',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
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
    weather: ''
  };

  constructor(private siteProgressService: SiteProgressService) {}

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
      weather: ''
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
