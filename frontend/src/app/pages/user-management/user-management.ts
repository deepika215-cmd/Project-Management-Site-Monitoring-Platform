import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface User {
  name: string;
  email: string;
  role: string;
  status: 'Active' | 'Inactive';
}

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [FormsModule, HttpClientModule],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagement implements OnInit {

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  showForm = false;

  users: User[] = [];

  newUser: User = {
    name: '',
    email: '',
    role: '',
    status: 'Active'
  };

  // Load users from backend
  loadUsers(): void {
    this.http.get<User[]>('http://127.0.0.1:8000/users')
      .subscribe({
        next: (data) => {
          this.users = data;
        },
        error: (error) => {
          console.error(error);
        }
      });
  }

  openForm(): void {
    this.showForm = true;
  }

  cancel(): void {
    this.showForm = false;

    this.newUser = {
      name: '',
      email: '',
      role: '',
      status: 'Active'
    };
  }

  addUser(): void {
    if (!this.newUser.name || !this.newUser.email || !this.newUser.role) {
      alert('Please fill in all required fields.');
      return;
    }

    this.http.post('http://127.0.0.1:8000/users', this.newUser)
      .subscribe({
        next: (response: any) => {
          // Reload users from database
          this.loadUsers();

          // Reset form
          this.cancel();

          alert('User saved to database successfully');
        },
        error: (error) => {
          console.error(error);
          alert('Failed to save user');
        }
      });
  }

  removeUser(email: string): void {
  const confirmed = confirm('Are you sure you want to remove this user?');

  if (confirmed) {
    this.http.delete(`http://127.0.0.1:8000/users/${email}`)
      .subscribe({
        next: () => {
          this.loadUsers(); // reload from database
          alert('User deleted successfully');
        },
        error: (error) => {
          console.error(error);
          alert('Failed to delete user');
        }
      });
    }
  }
}
