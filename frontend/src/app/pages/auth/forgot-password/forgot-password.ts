import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize, timeout } from 'rxjs';
import Swal from 'sweetalert2';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css'
})
export class ForgotPassword {

  email = '';
  submitting = false;
  devResetLink = '';
  infoMessage = '';

  constructor(private api: Api, private cdr: ChangeDetectorRef) {}

  resetPassword(): void {
    const email = this.email.trim().toLowerCase();
    this.devResetLink = '';
    this.infoMessage = '';

    if (!email) {
      Swal.fire({
        icon: 'warning',
        title: 'Email Required',
        text: 'Please enter your email address.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (!this.isValidEmail(email)) {
      Swal.fire({
        icon: 'error',
        title: 'Invalid Email',
        text: 'Please enter a valid email address.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    this.submitting = true;

    this.api.forgotPassword(email).pipe(
      timeout({ first: 12000 }),
      finalize(() => {
        this.submitting = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (res: any) => {
        this.devResetLink = res?.reset_link || '';
        this.infoMessage = res?.message || 'If an account with that email exists, a password reset link has been generated.';

        Swal.fire({
          icon: 'success',
          title: this.devResetLink ? 'Reset Link Generated' : 'Check Your Email',
          html: this.devResetLink
            ? `A local development reset link was generated.<br><br><input style="width:100%;padding:10px;border:1px solid #cbd5e1;border-radius:8px" readonly value="${this.devResetLink}">`
            : 'If an account with that email exists, a password reset link has been sent.',
          confirmButtonColor: '#2563eb'
        });

        this.email = '';
      },
      error: (error: any) => {
        Swal.fire({
          icon: 'error',
          title: 'Something Went Wrong',
          text: this.errorText(error),
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }

  copyResetLink(): void {
    if (!this.devResetLink) {
      return;
    }

    navigator.clipboard?.writeText(this.devResetLink).then(() => {
      Swal.fire({
        icon: 'success',
        title: 'Copied',
        text: 'Reset link copied to clipboard.',
        confirmButtonColor: '#2563eb'
      });
    });
  }

  isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  private errorText(error: any): string {
    if (error?.name === 'TimeoutError') {
      return 'Backend is taking too long to respond. Make sure FastAPI is running and try again.';
    }
    if (error?.status === 0) {
      return 'Cannot connect to the BuildTrack backend. Start FastAPI on http://localhost:8000 first.';
    }
    const detail = error?.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    return 'Unable to process your request right now. Please try again later.';
  }
}
