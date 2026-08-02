import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

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


  constructor(
    private router: Router
  ) {}


  login(): void {

    if (!this.email || !this.password) {

      alert(
        'Please enter your email and password.'
      );

      return;

    }


    if (!this.isValidEmail(this.email)) {

      alert(
        'Please enter a valid email address.'
      );

      return;

    }


    /*
      FRONTEND DEMO ONLY

      Later this will be replaced with
      an API call to your Spring Boot backend.

      The backend will authenticate the user,
      generate a JWT token and return the user's role.
    */


    const email = this.email.toLowerCase();


    if (email.includes('admin')) {

      this.router.navigate([
        '/admin-dashboard'
      ]);

    }

    else if (
      email.includes('manager')
    ) {

      this.router.navigate([
        '/project-manager-dashboard'
      ]);

    }

    else if (
      email.includes('engineer')
    ) {

      this.router.navigate([
        '/site-engineer-dashboard'
      ]);

    }

    else if (
      email.includes('contractor')
    ) {

      this.router.navigate([
        '/contractor-dashboard'
      ]);

    }

    else if (
      email.includes('worker')
    ) {

      this.router.navigate([
        '/worker-dashboard'
      ]);

    }

    else if (
      email.includes('client')
    ) {

      this.router.navigate([
        '/client-dashboard'
      ]);

    }

    else {

      alert(
        'Demo login: Use an email containing admin, manager, engineer, contractor, worker, or client.'
      );

    }

  }


  isValidEmail(
    email: string
  ): boolean {

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return emailPattern.test(email);

  }

}