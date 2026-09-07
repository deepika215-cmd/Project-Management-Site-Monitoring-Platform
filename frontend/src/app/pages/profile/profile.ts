import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, of, Subject, takeUntil, timeout } from 'rxjs';
import Swal from 'sweetalert2';

import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

interface CurrentUser {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  role: string;
  is_active?: boolean;
  isActive?: boolean;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css'],
})
export class Profile implements OnInit, OnDestroy {
  loading = false;
  errorMessage = '';
  user: CurrentUser | null = null;

  editMode = false;
  savingProfile = false;
  profileForm = { name: '', phone: '', email: '' };

  changingPassword = false;
  savingPassword = false;
  passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };

  private destroy$ = new Subject<void>();

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadProfile(): void {
    this.errorMessage = '';

    const cached = this.cachedUser();
    if (cached) {
      this.user = cached;
      this.resetProfileForm();
      this.loading = false;
      this.cdr.detectChanges();
    } else {
      this.loading = true;
    }

    this.api.getCurrentUser().pipe(
      timeout({ first: 8000 }),
      catchError((error: any) => {
        const fallback = this.cachedUser();
        if (fallback) {
          this.user = fallback;
          this.resetProfileForm();
          this.errorMessage = 'Live profile data could not be refreshed. Showing the last logged-in profile.';
        } else {
          this.errorMessage = this.errorText(error, 'Unable to load your profile right now.');
        }
        return of(null);
      }),
      finalize(() => {
        this.loading = false;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((data: any) => {
      if (!data) {
        return;
      }
      this.user = this.normalizeUser(data);
      localStorage.setItem('currentUser', JSON.stringify(this.user));
      this.resetProfileForm();
    });
  }

  resetProfileForm(): void {
    if (!this.user) {
      return;
    }

    this.profileForm = {
      name: this.user.name || '',
      phone: this.user.phone || '',
      email: this.user.email || ''
    };
  }

  startEdit(): void {
    this.resetProfileForm();
    this.editMode = true;
  }

  cancelEdit(): void {
    this.resetProfileForm();
    this.editMode = false;
  }

  saveProfile(): void {
    if (!this.profileForm.name?.trim() || !this.profileForm.email?.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Fields',
        text: 'Name and email are required.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    this.savingProfile = true;
    this.errorMessage = '';

    const payload = {
      name: this.profileForm.name.trim(),
      email: this.profileForm.email.trim(),
      phone: this.profileForm.phone?.trim() || null
    };

    this.api.updateProfile(payload).pipe(
      timeout({ first: 10000 }),
      catchError((error: any) => {
        this.errorMessage = this.errorText(error, 'Unable to update your profile.');
        Swal.fire({
          icon: 'error',
          title: 'Update Failed',
          text: this.errorMessage,
          confirmButtonColor: '#2563eb'
        });
        return of(null);
      }),
      finalize(() => {
        this.savingProfile = false;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((data: any) => {
      if (!data) {
        return;
      }

      this.user = this.normalizeUser(data);
      localStorage.setItem('currentUser', JSON.stringify(this.user));
      this.resetProfileForm();
      this.editMode = false;

      Swal.fire({
        icon: 'success',
        title: 'Profile Updated',
        confirmButtonColor: '#2563eb'
      });
    });
  }

  startChangePassword(): void {
    this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };
    this.changingPassword = true;
  }

  cancelChangePassword(): void {
    this.changingPassword = false;
  }

  submitPasswordChange(): void {
    const { currentPassword, newPassword, confirmPassword } = this.passwordForm;

    if (!currentPassword || !newPassword || !confirmPassword) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Fields',
        text: 'Please fill in all password fields.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (newPassword.length < 8) {
      Swal.fire({
        icon: 'warning',
        title: 'Password Too Short',
        text: 'New password must be at least 8 characters and include uppercase, lowercase, number and special character.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      Swal.fire({
        icon: 'error',
        title: 'Passwords Do Not Match',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    this.savingPassword = true;
    this.errorMessage = '';

    this.api.changePassword(currentPassword, newPassword).pipe(
      timeout({ first: 10000 }),
      catchError((error: any) => {
        const msg = this.errorText(error, 'Unable to change your password.');
        Swal.fire({
          icon: 'error',
          title: 'Password Change Failed',
          text: msg,
          confirmButtonColor: '#2563eb'
        });
        return of(null);
      }),
      finalize(() => {
        this.savingPassword = false;
        this.cdr.detectChanges();
      }),
      takeUntil(this.destroy$)
    ).subscribe((data: any) => {
      if (!data) {
        return;
      }

      this.changingPassword = false;
      this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };

      Swal.fire({
        icon: 'success',
        title: 'Password Changed',
        confirmButtonColor: '#2563eb'
      });
    });
  }

  private cachedUser(): CurrentUser | null {
    try {
      const cached = JSON.parse(localStorage.getItem('currentUser') || 'null');
      return cached?.id ? this.normalizeUser(cached) : null;
    } catch {
      return null;
    }
  }

  private normalizeUser(data: any): CurrentUser {
    return {
      id: Number(data?.id || 0),
      name: data?.name || data?.full_name || data?.fullName || 'User',
      email: data?.email || '',
      phone: data?.phone || '',
      role: data?.role || '',
      is_active: data?.is_active ?? data?.isActive ?? true,
      isActive: data?.is_active ?? data?.isActive ?? true
    };
  }

  private errorText(error: any, fallback: string): string {
    const detail = error?.error?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item: any) => item?.msg || item?.message || JSON.stringify(item)).join(' | ');
    }
    if (error?.status === 0) {
      return 'Backend is not responding. Start FastAPI on http://localhost:8000 and refresh this page.';
    }
    return fallback;
  }
}
