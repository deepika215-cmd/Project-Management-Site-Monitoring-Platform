import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class Api {

  private baseUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  // Login
  login(email: string, password: string) {

    const body = new URLSearchParams();

    body.set('username', email);
    body.set('password', password);

    return this.http.post(
      `${this.baseUrl}/auth/login`,
      body.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );

  }

  // Register
  register(user: any) {

    return this.http.post(
      `${this.baseUrl}/auth/register`,
      user
    );

  }

  // Logged-in user
  getCurrentUser() {

    const token = localStorage.getItem('token');

    return this.http.get(
      `${this.baseUrl}/auth/me`,
      {
        headers: new HttpHeaders({
          Authorization: `Bearer ${token}`
        })
      }
    );

  }

  // Get all users
  getUsers() {

    return this.http.get(
      `${this.baseUrl}/users`
    );

  }

  // Create user
  createUser(user: any) {

    return this.http.post(
      `${this.baseUrl}/users`,
      user
    );

  }

  // Delete user
  deleteUser(email: string) {

    return this.http.delete(
      `${this.baseUrl}/users/${email}`
    );

  }

}