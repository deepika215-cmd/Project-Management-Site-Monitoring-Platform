import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { finalize, timeout } from 'rxjs';
import Swal from 'sweetalert2';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink
  ],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class Register {

  fullName = '';
  email = '';
  mobile = '';
  employeeId = '';
  role = '';
  department = '';
  password = '';
  confirmPassword = '';
  address = '';

  submitting = false;
  showPassword = false;
  showConfirmPassword = false;

  constructor(
    private api: Api,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  register(): void {
    const fullName = this.fullName.trim();
    const email = this.email.trim().toLowerCase();
    const mobile = this.mobile.trim();
    const employeeId = this.employeeId.trim();
    const role = this.role.trim().toUpperCase();
    const department = this.department.trim();
    const address = this.address.trim();

    if (!fullName || !email || !mobile || !employeeId || !role || !this.password || !this.confirmPassword) {
      Swal.fire({
        icon: 'warning',
        title: 'Missing Information',
        text: 'Please fill all required fields.',
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

    if (!/^\d{7,15}$/.test(mobile.replace(/[\s+-]/g, ''))) {
      Swal.fire({
        icon: 'warning',
        title: 'Invalid Mobile Number',
        text: 'Please enter a valid mobile number with at least 7 digits.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (!this.isStrongPassword(this.password)) {
      Swal.fire({
        icon: 'warning',
        title: 'Weak Password',
        text: 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    if (this.password !== this.confirmPassword) {
      Swal.fire({
        icon: 'error',
        title: "Passwords Don't Match",
        text: 'Please make sure both passwords are the same.',
        confirmButtonColor: '#2563eb'
      });
      return;
    }

    const user = {
      name: fullName,
      email,
      password: this.password,
      phone: mobile,
      role,
      employee_id: employeeId,
      department: department || null,
      address: address || null
    };

    this.submitting = true;

    this.api.register(user).pipe(
      timeout({ first: 12000 }),
      finalize(() => {
        this.submitting = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: () => {
        Swal.fire({
          icon: 'success',
          title: 'Registration Successful!',
          text: 'Your account has been created successfully. You can now log in.',
          confirmButtonColor: '#2563eb'
        }).then(() => {
          this.router.navigate(['/login']);
        });
      },
      error: (err: any) => {
        Swal.fire({
          icon: 'error',
          title: 'Registration Failed',
          text: this.errorText(err, 'Something went wrong while creating the account.'),
          confirmButtonColor: '#2563eb'
        });
      }
    });
  }

  togglePassword(): void {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPassword(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  isStrongPassword(password: string): boolean {
    return password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[^A-Za-z0-9]/.test(password);
  }

  private errorText(err: any, fallback: string): string {
    const detail = err?.error?.detail;

    if (err?.name === 'TimeoutError') {
      return 'Backend is taking too long to respond. Make sure FastAPI is running on http://localhost:8000 and try again.';
    }

    if (err?.status === 0) {
      return 'Cannot connect to the BuildTrack backend. Start FastAPI on http://localhost:8000 first.';
    }

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item: any) => item?.msg || item?.message || JSON.stringify(item))
        .join('\n');
    }

    if (detail && typeof detail === 'object') {
      return detail.message || JSON.stringify(detail);
    }

    return fallback;
  }
}
