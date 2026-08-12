<<<<<<< HEAD
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize, timeout } from 'rxjs';
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

  constructor(
    private api: Api,
    private cdr: ChangeDetectorRef) { }

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    console.log('loadProfile() started');

    this.loading = true;
    this.errorMessage = '';

    this.api
      .getCurrentUser()
      .pipe(
        timeout({ each: 8000 }),
        finalize(() => {
          console.log('FINALIZE - setting loading to false');

          this.loading = false;

          // Force Angular to update the screen
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (data: any) => {
          console.log('Profile loaded:', data);

          this.user = data;

          this.resetProfileForm();

          localStorage.setItem(
            'currentUser',
            JSON.stringify(data)
          );

          this.cdr.detectChanges();
        },

        error: (error: any) => {
          console.error('Failed to load profile:', error);

          try {
            const cached = JSON.parse(
              localStorage.getItem('currentUser') || 'null'
            );

            if (cached && cached.id) {
              console.log('Using cached profile:', cached);

              this.user = cached;
              this.resetProfileForm();

              this.errorMessage =
                'Unable to refresh from the server. Showing your saved profile.';
            } else {
              this.user = null;

              this.errorMessage =
                error?.error?.detail ||
                'Unable to load your profile right now.';
            }
          } catch (cacheError) {
            console.error(
              'Failed to read cached profile:',
              cacheError
            );

            this.user = null;

            this.errorMessage =
              error?.error?.detail ||
              'Unable to load your profile right now.';
          }

          this.cdr.detectChanges();
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
      alert('Name and email are required.');
      return;
    }

    this.savingProfile = true;

    this.api.updateProfile(this.profileForm).subscribe({
      next: (data: any) => {
        console.log('1. API SUCCESS');
        console.log('2. Response:', data);

        // Update user data
        this.user = data;

        // Update cached user
        localStorage.setItem('currentUser', JSON.stringify(data));

        // Reset form values
        this.resetProfileForm();

        // IMPORTANT: update UI state FIRST
        this.savingProfile = false;
        this.editMode = false;

        console.log('3. savingProfile:', this.savingProfile);
        console.log('4. editMode:', this.editMode);

        // Force Angular to render the updated profile
        this.cdr.detectChanges();

        console.log('5. UI state updated');

        // Show success popup AFTER the UI has been updated
        Swal.fire({
          icon: 'success',
          title: 'Profile Updated',
          confirmButtonColor: '#2563eb',
          confirmButtonText: 'OK'
        });
      },

      error: (error: any) => {
        console.error('Profile update failed:', error);

        this.savingProfile = false;

        this.cdr.detectChanges();

        alert(
          error?.error?.detail ||
          'Unable to update your profile.'
        );
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
    const {
      currentPassword,
      newPassword,
      confirmPassword
    } = this.passwordForm;

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

    this.api.changePassword(
      currentPassword,
      newPassword
    ).subscribe({
      next: () => {
        console.log('Password change successful');

        // IMPORTANT:
        // Update the UI state BEFORE showing SweetAlert.
        this.savingPassword = false;
        this.changingPassword = false;

        // Clear password fields
        this.passwordForm = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        };

        // Force Angular to update the button/form
        this.cdr.detectChanges();

        console.log(
          'savingPassword:',
          this.savingPassword
        );

        console.log(
          'changingPassword:',
          this.changingPassword
        );

        Swal.fire({
          icon: 'success',
          title: 'Password Changed',
          confirmButtonColor: '#2563eb',
          confirmButtonText: 'OK'
        });
      },

      error: (error: any) => {
        console.error(
          'Failed to change password:',
          error
        );

        this.savingPassword = false;

        this.cdr.detectChanges();

        Swal.fire({
          icon: 'error',
          title: 'Password Change Failed',
          text:
            error?.error?.detail ||
            'Unable to change your password.',
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }
}
=======
import { Component } from '@angular/core';

@Component({
  selector: 'app-profile',
  imports: [],
  templateUrl: './profile.html',
  styleUrl: './profile.css',
})
export class Profile {}
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
