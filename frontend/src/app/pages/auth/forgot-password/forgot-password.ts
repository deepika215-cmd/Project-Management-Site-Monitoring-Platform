import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import Swal from 'sweetalert2';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink
  ],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css'
})
export class ForgotPassword {

  email = '';
  submitting = false;

  constructor(private api: Api) {}

  resetPassword(): void {

    if (!this.email) {

      Swal.fire({
        icon: 'warning',
        title: 'Email Required',
        text: 'Please enter your email address.',
        confirmButtonColor: '#2563eb'
      });

      return;
    }

    if (!this.isValidEmail(this.email)) {

      Swal.fire({
        icon: 'error',
        title: 'Invalid Email',
        text: 'Please enter a valid email address.',
        confirmButtonColor: '#2563eb'
      });

      return;
    }

    this.submitting = true;

    this.api.forgotPassword(this.email).subscribe({

      next: () => {
        this.submitting = false;

        // Backend always returns this same generic message whether or
        // not the email is registered, so we can't and shouldn't reveal
        // which case happened here.
        Swal.fire({
          icon: 'success',
          title: 'Check Your Email',
          text: 'If an account with that email exists, a password reset link has been sent.',
          confirmButtonColor: '#2563eb'
        });

        this.email = '';
      },

      error: (error: any) => {
        this.submitting = false;

        console.error('Forgot password request failed:', error);

        Swal.fire({
          icon: 'error',
          title: 'Something Went Wrong',
          text: 'Unable to process your request right now. Please try again later.',
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }

  isValidEmail(email: string): boolean {

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  }

}
