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

  // Selected user for View modal
  selectedUser: User | null = null;
  showView = false;

  // Loading/error state
  loading = false;
  errorMessage = '';

  // Add/Edit form state
  showForm = false;
  editingUser: User | null = null;

  // Search/filter
  searchTerm = '';
  roleFilter = '';

  // Form model
  formModel: UserFormModel = { ...EMPTY_FORM };

  // Available roles
  roles = [
    {
      value: 'ADMIN',
      label: 'Administrator'
    },
    {
      value: 'PROJECT_MANAGER',
      label: 'Project Manager'
    },
    {
      value: 'SITE_ENGINEER',
      label: 'Site Engineer'
    },
    {
      value: 'CONTRACTOR',
      label: 'Contractor'
    },
    {
      value: 'WORKER',
      label: 'Worker'
    },
    {
      value: 'CLIENT',
      label: 'Client'
    }
  ];

  constructor(private api: Api) { }

  ngOnInit(): void {
    this.loadUsers();
  }

  // ============================================================
  // LOAD USERS
  // ============================================================

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
          this.errorMessage =
            'You are not authorized. Please log in again.';
        } else if (error?.status === 403) {
          this.errorMessage =
            'You do not have permission to view users.';
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

  // ============================================================
  // FILTERED USERS
  // ============================================================

  get filteredUsers(): User[] {
    const term = this.searchTerm.trim().toLowerCase();

    return this.users.filter(user => {
      const matchesTerm =
        !term ||
        user.name?.toLowerCase().includes(term) ||
        user.email?.toLowerCase().includes(term);

      const matchesRole =
        !this.roleFilter ||
        user.role === this.roleFilter;

      return matchesTerm && matchesRole;
    });
  }

  onSearchChange(): void {
    // filteredUsers automatically updates
  }

  onRoleFilterChange(): void {
    // filteredUsers automatically updates
  }

  // ============================================================
  // VIEW USER
  // ============================================================

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

  // ============================================================
  // ADD USER
  // ============================================================

  openForm(): void {
    this.editingUser = null;
    this.formModel = { ...EMPTY_FORM };
    this.showForm = true;
  }

  // ============================================================
  // EDIT USER
  // ============================================================

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

  // ============================================================
  // CANCEL FORM
  // ============================================================

  cancel(): void {
    this.showForm = false;
    this.editingUser = null;
    this.formModel = { ...EMPTY_FORM };
  }

  // ============================================================
  // CHECK IF EDITING
  // ============================================================

  get isEditing(): boolean {
    return this.editingUser !== null;
  }

  // ============================================================
  // ADD / UPDATE USER
  // ============================================================

  saveUser(): void {

    // Validate required fields
    if (
      !this.formModel.name ||
      !this.formModel.email ||
      !this.formModel.role
    ) {
      alert('Please fill in all required fields.');
      return;
    }

    // Password is required only when creating a new user
    if (!this.isEditing && !this.formModel.password) {
      alert('Please set a password for the new user.');
      return;
    }

    // ==========================================================
    // UPDATE EXISTING USER
    // ==========================================================

    if (this.isEditing) {

      const payload: any = {
        name: this.formModel.name,
        email: this.formModel.email,
        phone: this.formModel.phone,
        role: this.formModel.role
      };

      // Only send password when admin entered a new password
      if (this.formModel.password) {
        payload.password = this.formModel.password;
      }

      this.api.updateUser(
        this.editingUser!.id,
        payload
      ).subscribe({

        next: (updatedUser: any) => {

          console.log('User updated:', updatedUser);

          /*
           * Update the user immediately in the current UI.
           * This prevents the table from showing old information
           * until a page reload.
           */
          if (updatedUser) {
            this.users = this.users.map(user =>
              user.id === updatedUser.id
                ? updatedUser
                : user
            );

            /*
             * If the backend response does not contain the full
             * user object, update the existing object manually.
             */
          } else {
            this.users = this.users.map(user =>
              user.id === this.editingUser!.id
                ? {
                  ...user,
                  name: this.formModel.name,
                  email: this.formModel.email,
                  phone: this.formModel.phone,
                  role: this.formModel.role
                }
                : user
            );
          }

          // Close form
          this.cancel();

          // Refresh backend data
          this.loadUsers();
        },

        error: (error: any) => {

          console.error(
            'Failed to update user:',
            error
          );

          alert(
            error?.error?.detail ||
            error?.error?.message ||
            'Failed to update user.'
          );
        }

      });

      return;
    }

    // ==========================================================
    // CREATE NEW USER
    // ==========================================================

    this.api.createUser(this.formModel).subscribe({

      next: (createdUser: any) => {

        console.log('User created:', createdUser);

        /*
         * Add the new user immediately to the table.
         */
        if (createdUser) {
          this.users = [
            ...this.users,
            createdUser
          ];
        }

        // Close form
        this.cancel();

        // Refresh from backend
        this.loadUsers();
      },

      error: (error: any) => {

        console.error(
          'Failed to create user:',
          error
        );

        alert(
          error?.error?.detail ||
          error?.error?.message ||
          'Failed to add user.'
        );
      }

    });
  }

  // ============================================================
  // TOGGLE ACTIVE / INACTIVE
  // ============================================================

  toggleStatus(user: User): void {

    const newStatus = !user.is_active;

    this.api.updateUser(
      user.id,
      {
        is_active: newStatus
      }
    ).subscribe({

      next: (updatedUser: any) => {

        console.log(
          'User status updated:',
          updatedUser
        );

        /*
         * Update the status immediately in the UI.
         */
        this.users = this.users.map(existingUser =>
          existingUser.id === user.id
            ? {
              ...existingUser,
              is_active:
                updatedUser?.is_active ??
                newStatus
            }
            : existingUser
        );

        /*
         * If the user is currently open in the View modal,
         * update that object too.
         */
        if (
          this.selectedUser &&
          this.selectedUser.id === user.id
        ) {
          this.selectedUser = {
            ...this.selectedUser,
            is_active:
              updatedUser?.is_active ??
              newStatus
          };
        }

        // Synchronize with backend
        this.loadUsers();
      },

      error: (error: any) => {

        console.error(
          'Failed to update user status:',
          error
        );

        alert(
          error?.error?.detail ||
          error?.error?.message ||
          'Failed to update user status.'
        );
      }

    });
  }

  // ============================================================
  // DELETE USER
  // ============================================================

  removeUser(user: User): void {

    const confirmed = confirm(
      `Are you sure you want to delete ${user.name}?`
    );

    if (!confirmed) {
      return;
    }

    this.api.deleteUser(user.id).subscribe({

      next: () => {

        console.log(
          'User deleted:',
          user.id
        );

        /*
         * Remove immediately from the UI.
         */
        this.users = this.users.filter(
          existingUser =>
            existingUser.id !== user.id
        );

        /*
         * If this user is currently being viewed,
         * close the View modal.
         */
        if (
          this.selectedUser?.id === user.id
        ) {
          this.closeView();
        }
      },

      error: (error: any) => {

        console.error(
          'Failed to delete user:',
          error
        );

        alert(
          error?.error?.detail ||
          error?.error?.message ||
          'Failed to delete user.'
        );
      }

    });
  }
}