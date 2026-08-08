import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api } from '../../services/api';

interface User {
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagement implements OnInit {

  showForm = false;

  users: User[] = [];

  newUser = {
    name: '',
    email: '',
    role: ''
  };

  constructor(private api: Api) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {

    this.api.getUsers().subscribe({

      next: (data: any) => {

        console.log('Users received from backend:', data);

        this.users = data;

        console.log('Number of users:', this.users.length);

      },

      error: (error: any) => {

        console.error('Failed to load users:', error);

        alert('Unable to load users from the backend.');

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
      role: ''
    };

  }

  addUser(): void {

    if (
      !this.newUser.name ||
      !this.newUser.email ||
      !this.newUser.role
    ) {

      alert('Please fill in all required fields.');

      return;

    }

    this.api.createUser(this.newUser).subscribe({

      next: () => {

        alert('User added successfully.');

        this.cancel();

        this.loadUsers();

      },

      error: (error: any) => {

        console.error('Failed to create user:', error);

        alert('Failed to add user.');

      }

    });

  }

  removeUser(email: string): void {

    const confirmed = confirm(
      'Are you sure you want to delete this user?'
    );

    if (!confirmed) {
      return;
    }

    this.api.deleteUser(email).subscribe({

      next: () => {

        alert('User deleted successfully.');

        this.loadUsers();

      },

      error: (error: any) => {

        console.error('Failed to delete user:', error);

        alert('Failed to delete user.');

      }

    });

  }

}