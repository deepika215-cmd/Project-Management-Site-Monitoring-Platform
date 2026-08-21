import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
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

  constructor(
  private api: Api,
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

    const user = {
  name: this.fullName,
  email: this.email,
  password: this.password,
  phone: this.mobile,
  role: this.role
};

this.api.register(user).subscribe({

  next: () => {

    Swal.fire({
      icon: 'success',
      title: 'Registration Successful!',
      text: 'Your account has been created successfully.',
      confirmButtonColor: '#2563eb'
    }).then(() => {

      this.router.navigate(['/login']);

    });

  },

  error: (err) => {

    Swal.fire({
      icon: 'error',
      title: 'Registration Failed',
      text: err.error.detail || 'Something went wrong.',
      confirmButtonColor: '#2563eb'
    });

  }

});

  }

  isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

}