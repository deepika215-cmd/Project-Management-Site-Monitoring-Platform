import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Api } from '../../../services/api';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule,
    RouterLink
  ],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login {

  email = '';
  password = '';
  rememberMe = false;
  showPassword = false;

  constructor(
    private router: Router,
    private api: Api
  ) {}

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  login(): void {

    if (!this.email || !this.password) {
      alert('Please enter your email and password.');
      return;
    }

    if (!this.isValidEmail(this.email)) {
      alert('Please enter a valid email address.');
      return;
    }

    this.api.login(this.email, this.password).subscribe({

      next: (response: any) => {

        // Save JWT
        localStorage.setItem(
          'token',
          response.access_token
        );

        // Fetch logged-in user
        this.api.getCurrentUser().subscribe({

          next: (user: any) => {

            localStorage.setItem('currentUser', JSON.stringify(user));
            console.log('Logged-in user:', user);
            console.log('User role:', user.role);

            // Convert role to uppercase so
            // "admin" and "ADMIN" both work
            const role = user.role?.toUpperCase();

            switch (role) {

              case 'ADMIN':
                this.router.navigate(['/admin-dashboard']);
                break;

              case 'PROJECT_MANAGER':
                this.router.navigate(['/project-manager-dashboard']);
                break;

              case 'SITE_ENGINEER':
                this.router.navigate(['/site-engineer-dashboard']);
                break;

              case 'CONTRACTOR':
                this.router.navigate(['/contractor-dashboard']);
                break;

              case 'WORKER':
                this.router.navigate(['/worker-dashboard']);
                break;

              case 'CLIENT':
                this.router.navigate(['/client-dashboard']);
                break;

              default:
                console.error(
                  'Unknown role received from backend:',
                  user.role
                );

                alert('Unknown role: ' + user.role);
            }

          },

          error: (err: any) => {

            console.error('Error fetching current user:', err);
            alert('Unable to fetch user details.');

          }

        });

      },

      error: (err: any) => {

        console.error('Login error:', err);

        if (err?.status === 0) {
          alert('Cannot connect to the BuildTrack backend. Make sure FastAPI is running on http://localhost:8000.');
          return;
        }

        const detail = err?.error?.detail;
        if (typeof detail === 'string' && detail.trim()) {
          alert(detail);
          return;
        }

        if (Array.isArray(detail)) {
          const message = detail
            .map((item: any) => item?.msg || item?.message || JSON.stringify(item))
            .join('\n');
          alert(message || 'Login request was rejected by the backend.');
          return;
        }

        alert(`Login failed (HTTP ${err?.status ?? 'unknown'}). Please check the backend terminal.`);

      }

    });

  }

  isValidEmail(email: string): boolean {

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return emailPattern.test(email);
  }

}

