import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface User {
  name: string;
  email: string;
  role: string;
  status: 'Active' | 'Inactive';
}

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagement {
  showForm = false;

  users: User[] = [
    {
      name: 'Selva Kumar',
      email: 'selva@example.com',
      role: 'Administrator',
      status: 'Active'
    },
    {
      name: 'John David',
      email: 'john@example.com',
      role: 'Project Manager',
      status: 'Active'
    },
    {
      name: 'Priya Sharma',
      email: 'priya@example.com',
      role: 'Site Engineer',
      status: 'Inactive'
    }
  ];

  newUser: User = {
    name: '',
    email: '',
    role: '',
    status: 'Active'
  };

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

    this.users.push({ ...this.newUser });
    this.cancel();
  }

  removeUser(email: string): void {
    const confirmed = confirm('Are you sure you want to remove this user?');

    if (confirmed) {
      this.users = this.users.filter(user => user.email !== email);
    }
  }
}