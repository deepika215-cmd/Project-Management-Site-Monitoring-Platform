import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { finalize, timeout } from 'rxjs';
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
  tokenPresent = true;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: Api,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
    this.tokenPresent = !!this.token;
  }

  submit(): void {
    if (!this.tokenPresent || !this.token) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Reset Link',
        text: 'Please request a new password reset link.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (!this.newPassword || !this.confirmPassword) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Fields',
        text: 'Please fill in both password fields.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (!this.isStrongPassword(this.newPassword)) {
      Swal.fire({
        icon: 'warning',
        title: 'Weak Password',
        text: 'Password must be at least 8 characters and include uppercase, lowercase, number and special character.',
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

    this.api.resetPassword(this.token, this.newPassword).pipe(
      timeout({ first: 12000 }),
      finalize(() => {
        this.submitting = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
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
        Swal.fire({
          icon: 'error',
          title: 'Link Invalid or Expired',
          text: this.errorText(error),
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }

  toggleNewPassword(): void {
    this.showNewPassword = !this.showNewPassword;
  }

  toggleConfirmPassword(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  private isStrongPassword(password: string): boolean {
    return password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[^A-Za-z0-9]/.test(password);
  }

  private errorText(error: any): string {
    if (error?.name === 'TimeoutError') {
      return 'Backend is taking too long to respond. Please try again.';
    }
    if (error?.status === 0) {
      return 'Cannot connect to the BuildTrack backend. Start FastAPI on http://localhost:8000 first.';
    }
    return error?.error?.detail || 'Please request a new password reset link.';
  }
}
