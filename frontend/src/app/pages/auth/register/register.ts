import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import Swal from 'sweetalert2';

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

  constructor(
    private router: Router
  ) {}

  register(): void {

    if (
      !this.fullName ||
      !this.email ||
      !this.mobile ||
      !this.employeeId ||
      !this.role ||
      !this.password ||
      !this.confirmPassword
    ) {

      Swal.fire({
        icon: 'warning',
        title: 'Missing Information',
        text: 'Please fill all required fields.',
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

    if (this.password.length < 8) {

      Swal.fire({
        icon: 'warning',
        title: 'Weak Password',
        text: 'Password must contain at least 8 characters.',
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

    Swal.fire({
      icon: 'success',
      title: 'Registration Successful!',
      text: 'Your account has been created successfully.',
      confirmButtonText: 'Go to Login',
      confirmButtonColor: '#2563eb'
    }).then(() => {
      this.router.navigate(['/login']);
    });

  }

  isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

}