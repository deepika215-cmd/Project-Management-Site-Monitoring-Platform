import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import Swal from 'sweetalert2';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink
  ],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.css'
})
export class ResetPassword implements OnInit {

  token = '';
  newPassword = '';
  confirmPassword = '';
  submitting = false;

  // False if the page was opened without a ?token= in the URL —
  // there's nothing this page can do in that case except send the
  // person back to request a fresh link.
  tokenPresent = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: Api
  ) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
    this.tokenPresent = !!this.token;
  }

  submit(): void {

    if (!this.newPassword || !this.confirmPassword) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Fields',
        text: 'Please fill in both password fields.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (this.newPassword.length < 6) {
      Swal.fire({
        icon: 'warning',
        title: 'Password Too Short',
        text: 'Password must be at least 6 characters.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      Swal.fire({
        icon: 'error',
        title: 'Passwords Do Not Match',
        text: 'Please make sure both passwords match.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    this.submitting = true;

    this.api.resetPassword(this.token, this.newPassword).subscribe({

      next: () => {
        this.submitting = false;

        Swal.fire({
          icon: 'success',
          title: 'Password Reset',
          text: 'Your password has been updated. Please log in.',
          confirmButtonColor: '#2563eb'
        }).then(() => {
          this.router.navigate(['/login']);
        });
      },

      error: (error: any) => {
        this.submitting = false;

        console.error('Reset password failed:', error);

        Swal.fire({
          icon: 'error',
          title: 'Link Invalid or Expired',
          text: error?.error?.detail || 'Please request a new password reset link.',
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }
}
