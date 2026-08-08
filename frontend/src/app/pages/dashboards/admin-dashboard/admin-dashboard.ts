import { Component } from '@angular/core';
<<<<<<< HEAD
import { Router, RouterLink } from '@angular/router';
import Swal from 'sweetalert2';
=======
import { RouterLink } from '@angular/router';
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    RouterLink
  ],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css'
})
export class AdminDashboard {

<<<<<<< HEAD
  constructor(private router: Router) {}

  logout(): void {

    localStorage.removeItem('token');

    Swal.fire({
      icon: 'success',
      title: 'Logged Out',
      text: 'You have been logged out successfully.',
      confirmButtonColor: '#2563eb'
    }).then(() => {

      this.router.navigate(['/login']);

    });

  }

=======
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242
}