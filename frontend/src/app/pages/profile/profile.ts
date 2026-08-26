import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { timeout } from 'rxjs';
import Swal from 'sweetalert2';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

interface CurrentUser {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: string;
  is_active: boolean;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, AppSidebarComponent],
  templateUrl: './profile.html',
  styleUrl: './profile.css',
})
export class Profile implements OnInit {

  loading = true;
  errorMessage = '';
  user: CurrentUser | null = null;

  // Editable copies, kept separate from `user` so "Cancel" can discard
  // in-progress edits without re-fetching from the server.
  editMode = false;
  savingProfile = false;
  profileForm = { name: '', phone: '', email: '' };

  changingPassword = false;
  savingPassword = false;
  passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.getCurrentUser().pipe(timeout({ each: 8000 })).subscribe({
      next: (data: any) => {
        this.user = data;
        this.resetProfileForm();
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Failed to load profile:', error);
        // Keep the profile usable when /auth/me is temporarily unavailable.
        // Login already stores the authenticated user locally.
        try {
          const cached = JSON.parse(localStorage.getItem('currentUser') || 'null');
          if (cached && cached.id) {
            this.user = cached;
            this.resetProfileForm();
            this.errorMessage = 'Live profile data could not be refreshed. Showing the last authenticated profile.';
          } else {
            this.errorMessage = error?.error?.detail || 'Unable to load your profile right now.';
          }
        } catch {
          this.errorMessage = error?.error?.detail || 'Unable to load your profile right now.';
        }
        this.loading = false;
      }
    });
  }

  resetProfileForm(): void {
    if (!this.user) {
      return;
    }

    this.profileForm = {
      name: this.user.name,
      phone: this.user.phone || '',
      email: this.user.email
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

    if (!this.profileForm.name || !this.profileForm.email) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Fields',
        text: 'Name and email are required.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    this.savingProfile = true;

    this.api.updateProfile(this.profileForm).subscribe({
      next: (data: any) => {
        this.savingProfile = false;
        this.user = data;
        localStorage.setItem('currentUser', JSON.stringify(data));
        this.editMode = false;

        Swal.fire({
          icon: 'success',
          title: 'Profile Updated',
          confirmButtonColor: '#2563eb'
        });
      },
      error: (error: any) => {
        this.savingProfile = false;
        console.error('Failed to update profile:', error);

        Swal.fire({
          icon: 'error',
          title: 'Update Failed',
          text: error?.error?.detail || 'Unable to update your profile.',
          confirmButtonColor: '#2563eb'
        });
      }
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

    if (newPassword.length < 6) {
      Swal.fire({
        icon: 'warning',
        title: 'Password Too Short',
        text: 'New password must be at least 6 characters.',
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

    this.api.changePassword(currentPassword, newPassword).subscribe({
      next: () => {
        this.savingPassword = false;
        this.changingPassword = false;

        Swal.fire({
          icon: 'success',
          title: 'Password Changed',
          confirmButtonColor: '#2563eb'
        });
      },
      error: (error: any) => {
        this.savingPassword = false;
        console.error('Failed to change password:', error);

        Swal.fire({
          icon: 'error',
          title: 'Password Change Failed',
          text: error?.error?.detail || 'Unable to change your password.',
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }
}
