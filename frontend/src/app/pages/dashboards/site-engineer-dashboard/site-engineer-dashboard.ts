import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-site-engineer-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './site-engineer-dashboard.html',
  styleUrl: './site-engineer-dashboard.css'
})
export class SiteEngineerDashboard {}