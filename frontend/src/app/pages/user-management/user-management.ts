import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: string;
  is_active: boolean;
}

interface UserFormModel {
  name: string;
  email: string;
  phone: string;
  role: string;
  password: string;
}

const EMPTY_FORM: UserFormModel = {
  name: '',
  email: '',
  phone: '',
  role: '',
  password: ''
};

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [FormsModule, AppSidebarComponent],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagement implements OnInit {

  // All users loaded from the backend
  users: User[] = [];

  // Users after search/role filtering, what the table actually renders
  selectedUser: User | null = null;
  showView = false;

  loading = false;
  errorMessage = '';

  showForm = false;
  editingUser: User | null = null;

  searchTerm = '';
  roleFilter = '';

  formModel: UserFormModel = { ...EMPTY_FORM };

  roles = [
    { value: 'ADMIN', label: 'Administrator' },
    { value: 'PROJECT_MANAGER', label: 'Project Manager' },
    { value: 'SITE_ENGINEER', label: 'Site Engineer' },
    { value: 'CONTRACTOR', label: 'Contractor' },
    { value: 'WORKER', label: 'Worker' },
    { value: 'CLIENT', label: 'Client' }
  ];

  constructor(private api: Api) { }

  ngOnInit(): void {
    this.loadUsers();
  }

  // Load users from backend
  loadUsers(): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.getUsers().subscribe({
      next: (data: any) => {
        console.log('GET /users/ response:', data);

        if (Array.isArray(data)) {
          this.users = data;
        } else if (Array.isArray(data?.users)) {
          this.users = data.users;
        } else if (Array.isArray(data?.data)) {
          this.users = data.data;
        } else {
          this.users = [];
        }

        console.log('Users loaded:', this.users);

        this.loading = false;
      },

      error: (error: any) => {
        console.error('GET /users/ failed:', error);

        this.users = [];
        this.loading = false;

        if (error?.status === 401) {
          this.errorMessage = 'You are not authorized. Please log in again.';
        } else if (error?.status === 403) {
          this.errorMessage = 'You do not have permission to view users.';
        } else if (error?.status === 0) {
          this.errorMessage =
            'Cannot connect to the backend. Make sure the backend server is running.';
        } else {
          this.errorMessage =
            error?.error?.detail ||
            error?.error?.message ||
            'Unable to load users from the backend.';
        }
      }
    });
  }

  // Always derive the displayed list from the current users + filters.
  // This prevents the table from appearing empty until a filter is changed.
  get filteredUsers(): User[] {
    const term = this.searchTerm.trim().toLowerCase();

    return this.users.filter(user => {
      const matchesTerm =
        !term ||
        user.name?.toLowerCase().includes(term) ||
        user.email?.toLowerCase().includes(term);

      const matchesRole = !this.roleFilter || user.role === this.roleFilter;
      return matchesTerm && matchesRole;
    });
  }

  onSearchChange(): void { }

  onRoleFilterChange(): void { }

  openView(user: User): void {
    this.selectedUser = user;
    this.showView = true;
  }

  closeView(): void {
    this.showView = false;
    this.selectedUser = null;
  }

  editSelectedUser(): void {
    if (!this.selectedUser) {
      return;
    }

    const user = this.selectedUser;

    this.closeView();
    this.openEditForm(user);
  }

  // Open the form to add a brand-new user
  openForm(): void {
    this.editingUser = null;
    this.formModel = { ...EMPTY_FORM };
    this.showForm = true;
  }

  // Open the form pre-filled to edit an existing user
  openEditForm(user: User): void {
    this.editingUser = user;
    this.formModel = {
      name: user.name,
      email: user.email,
      phone: user.phone || '',
      role: user.role,
      password: ''
    };
    this.showForm = true;
  }

  cancel(): void {
    this.showForm = false;
    this.editingUser = null;
    this.formModel = { ...EMPTY_FORM };
  }

  get isEditing(): boolean {
    return this.editingUser !== null;
  }

  // Add or update, depending on whether we're editing
  saveUser(): void {

    if (!this.formModel.name || !this.formModel.email || !this.formModel.role) {
      alert('Please fill in all required fields.');
      return;
    }

    if (!this.isEditing && !this.formModel.password) {
      alert('Please set a password for the new user.');
      return;
    }

    if (this.isEditing) {
      // Only send a password if the admin actually typed a new one
      const payload: any = {
        name: this.formModel.name,
        email: this.formModel.email,
        phone: this.formModel.phone,
        role: this.formModel.role
      };

      if (this.formModel.password) {
        payload.password = this.formModel.password;
      }

      this.api.updateUser(this.editingUser!.id, payload).subscribe({
        next: () => {
          this.cancel();
          this.loadUsers();
        },
        error: (error: any) => {
          console.error('Failed to update user:', error);
          alert(error?.error?.detail || 'Failed to update user.');
        }
      });

    } else {

      this.api.createUser(this.formModel).subscribe({
        next: () => {
          this.cancel();
          this.loadUsers();
        },
        error: (error: any) => {
          console.error('Failed to create user:', error);
          alert(error?.error?.detail || 'Failed to add user.');
        }
      });
    }
  }

  // Toggle active/inactive from the table without opening the full form
  toggleStatus(user: User): void {
    this.api.updateUser(user.id, { is_active: !user.is_active }).subscribe({
      next: () => this.loadUsers(),
      error: (error: any) => {
        console.error('Failed to update user status:', error);
        alert('Failed to update user status.');
      }
    });
  }

  // Delete user
  removeUser(user: User): void {
    const confirmed = confirm(
      `Are you sure you want to delete ${user.name}?`
    );

    if (!confirmed) {
      return;
    }

    this.api.deleteUser(user.id).subscribe({
      next: () => {
        // Remove the user immediately from the current UI
        this.users = this.users.filter(u => u.id !== user.id);

        // If this user was being viewed, close the view
        if (this.selectedUser?.id === user.id) {
          this.closeView();
        }
      },

      error: (error: any) => {
        console.error('Failed to delete user:', error);
        alert(error?.error?.detail || 'Failed to delete user.');
      }
    });
  }
}
