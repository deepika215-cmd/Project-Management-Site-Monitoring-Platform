import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
<<<<<<< HEAD
import { Api } from '../../services/api';
=======
import { HttpClient, HttpClientModule } from '@angular/common/http';
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242

interface User {
  name: string;
  email: string;
  role: string;
<<<<<<< HEAD
  is_active: boolean;
=======
  status: 'Active' | 'Inactive';
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242
}

@Component({
  selector: 'app-user-management',
  standalone: true,
<<<<<<< HEAD
  imports: [FormsModule],
=======
  imports: [FormsModule, HttpClientModule],
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagement implements OnInit {

<<<<<<< HEAD
  showForm = false;

  users: User[] = [];

  newUser = {
    name: '',
    email: '',
    role: ''
  };

  constructor(private api: Api) {}
=======
  constructor(private http: HttpClient) {}
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242

  ngOnInit(): void {
    this.loadUsers();
  }

<<<<<<< HEAD
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

=======
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
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242
  }

  openForm(): void {
    this.showForm = true;
  }

  cancel(): void {
<<<<<<< HEAD

=======
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242
    this.showForm = false;

    this.newUser = {
      name: '',
      email: '',
<<<<<<< HEAD
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
=======
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
>>>>>>> dea0b03a8b5bb7a945a9c80d1f323fcfd5e53242
