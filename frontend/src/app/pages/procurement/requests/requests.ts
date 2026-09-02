import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

@Component({
  selector: 'app-procurement-requests',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AppSidebarComponent
  ],
  templateUrl: './requests.html',
  styleUrl: './requests.css'
})
export class Requests implements OnInit {

  // =====================================================
  // DATA
  // =====================================================

  requests: any[] = [];
  projects: any[] = [];

  loading = false;
  saving = false;
  deleting = false;
  projectSaving = false;

  error = '';
  success = '';

  showForm = false;
  showProjectModal = false;

  editingId: number | null = null;


  // =====================================================
  // PROCUREMENT REQUEST FORM
  // =====================================================

  form = {
    project_id: 0,
    requested_by: '',
    item_name: '',
    category: 'Raw Materials',
    quantity: 1,
    required_date: '',
    purpose: '',
    priority: 'Medium',
    status: 'Pending',
    remarks: ''
  };


  // =====================================================
  // ADD PROJECT FORM
  // =====================================================

  projectForm = {
    project_name: '',
    description: '',
    status: 'Planning'
  };


  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(private api: Api) {}


  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {
    this.loadRequests();
    this.loadProjects();
  }


  // =====================================================
  // ERROR HANDLER
  // =====================================================

  private getErrorMessage(
    error: any,
    defaultMessage: string
  ): string {

    // -----------------------------------------------
    // 1. Null / undefined
    // -----------------------------------------------

    if (!error) {
      return defaultMessage;
    }


    // -----------------------------------------------
    // 2. Angular HttpErrorResponse
    // -----------------------------------------------

    const errorBody = error?.error;


    // -----------------------------------------------
    // 3. FastAPI simple detail string
    // Example:
    // {"detail":"Project not found"}
    // -----------------------------------------------

    if (typeof errorBody?.detail === 'string') {
      return errorBody.detail;
    }


    // -----------------------------------------------
    // 4. Normal message string
    // -----------------------------------------------

    if (typeof errorBody?.message === 'string') {
      return errorBody.message;
    }


    // -----------------------------------------------
    // 5. FastAPI validation error
    //
    // Example:
    // {
    //   "detail": [
    //      {
    //        "loc": ["body", "project_id"],
    //        "msg": "Field required",
    //        "type": "missing"
    //      }
    //   ]
    // }
    // -----------------------------------------------

    if (Array.isArray(errorBody?.detail)) {

      const messages = errorBody.detail
        .map((item: any) => {

          if (typeof item === 'string') {
            return item;
          }

          if (item?.msg) {

            const location =
              Array.isArray(item?.loc)
                ? item.loc
                    .filter(
                      (x: any) =>
                        x !== 'body' &&
                        x !== 'query' &&
                        x !== 'path'
                    )
                    .join(' → ')
                : '';

            if (location) {
              return `${location}: ${item.msg}`;
            }

            return item.msg;
          }

          return '';
        })
        .filter(
          (message: string) =>
            message.trim() !== ''
        );

      if (messages.length > 0) {
        return messages.join('\n');
      }
    }


    // -----------------------------------------------
    // 6. Backend errors object
    // -----------------------------------------------

    if (
      errorBody?.errors &&
      typeof errorBody.errors === 'object'
    ) {

      const messages: string[] = [];

      Object.keys(errorBody.errors).forEach(
        (key: string) => {

          const value =
            errorBody.errors[key];

          if (Array.isArray(value)) {

            value.forEach((item: any) => {

              if (typeof item === 'string') {
                messages.push(
                  `${key}: ${item}`
                );
              }
              else if (item?.msg) {
                messages.push(
                  `${key}: ${item.msg}`
                );
              }
              else {
                messages.push(
                  `${key}: ${this.safeString(item)}`
                );
              }

            });

          }
          else if (
            typeof value === 'string'
          ) {

            messages.push(
              `${key}: ${value}`
            );

          }
          else {

            messages.push(
              `${key}: ${this.safeString(value)}`
            );

          }

        }
      );

      if (messages.length > 0) {
        return messages.join('\n');
      }
    }


    // -----------------------------------------------
    // 7. Direct string error
    // -----------------------------------------------

    if (typeof error === 'string') {
      return error;
    }


    // -----------------------------------------------
    // 8. Angular status text
    // -----------------------------------------------

    if (
      error?.status &&
      error?.statusText &&
      error.statusText !== 'Unknown Error'
    ) {

      return `${error.status}: ${error.statusText}`;
    }


    // -----------------------------------------------
    // 9. Network error
    // -----------------------------------------------

    if (
      error?.status === 0 ||
      error?.message === 'Failed to fetch'
    ) {

      return 'Unable to connect to the backend. Please make sure the FastAPI server is running on http://localhost:8000.';
    }


    // -----------------------------------------------
    // 10. Error.message
    // -----------------------------------------------

    if (
      typeof error?.message === 'string' &&
      error.message.trim() !== ''
    ) {

      return error.message;
    }


    // -----------------------------------------------
    // 11. Last fallback
    // -----------------------------------------------

    return defaultMessage;
  }


  // =====================================================
  // SAFE OBJECT TO STRING
  // =====================================================

  private safeString(value: any): string {

    if (value === null || value === undefined) {
      return '';
    }

    if (typeof value === 'string') {
      return value;
    }

    if (typeof value === 'number' || typeof value === 'boolean') {
      return String(value);
    }

    try {
      return JSON.stringify(value);
    }
    catch {
      return String(value);
    }
  }


  // =====================================================
  // LOAD REQUESTS
  // =====================================================

  loadRequests(): void {

    this.loading = true;
    this.error = '';

    this.api.getProcurementRequests().subscribe({

      next: (rows: any) => {

        this.requests =
          Array.isArray(rows)
            ? rows
            : [];

        this.loading = false;

      },

      error: (e: any) => {

        this.loading = false;

        this.requests = [];

        this.error =
          this.getErrorMessage(
            e,
            'Unable to load procurement requests.'
          );

      }

    });

  }


  // =====================================================
  // LOAD PROJECTS
  // =====================================================

  loadProjects(): void {

    this.api.getProjects().subscribe({

      next: (rows: any) => {

        this.projects =
          Array.isArray(rows)
            ? rows
            : [];

      },

      error: (e: any) => {

        this.projects = [];

        this.error =
          this.getErrorMessage(
            e,
            'Unable to load projects.'
          );

      }

    });

  }


  // =====================================================
  // OPEN CREATE REQUEST FORM
  // =====================================================

  openCreate(): void {

    this.editingId = null;

    this.form = {

      project_id:
        Number(
          this.projects[0]?.id || 0
        ),

      requested_by: '',

      item_name: '',

      category: 'Raw Materials',

      quantity: 1,

      required_date: '',

      purpose: '',

      priority: 'Medium',

      status: 'Pending',

      remarks: ''

    };

    this.showForm = true;

    this.error = '';
    this.success = '';

  }


  // =====================================================
  // EDIT REQUEST
  // =====================================================

  edit(request: any): void {

    const id =
      Number(request?.id);

    if (!id) {

      this.error =
        'Invalid procurement request ID.';

      return;

    }

    this.editingId = id;

    this.form = {

      project_id:
        Number(
          request?.project_id
        ) || 0,

      requested_by:
        request?.requested_by || '',

      item_name:
        request?.item_name ||
        request?.item_material ||
        request?.item ||
        '',

      category:
        request?.category ||
        'Raw Materials',

      quantity:
        Number(
          request?.quantity ||
          request?.required_quantity
        ) || 1,

      required_date:
        request?.required_date || '',

      purpose:
        request?.purpose ||
        request?.requirement ||
        '',

      priority:
        request?.priority ||
        'Medium',

      status:
        request?.status ||
        'Pending',

      remarks:
        request?.remarks ||
        ''

    };

    this.showForm = true;

    this.error = '';
    this.success = '';

  }


  // =====================================================
  // CANCEL REQUEST FORM
  // =====================================================

  cancel(): void {

    if (this.saving) {
      return;
    }

    this.showForm = false;

    this.editingId = null;

    this.error = '';

  }


  // =====================================================
  // SAVE PROCUREMENT REQUEST
  // =====================================================

  save(): void {

    this.error = '';
    this.success = '';

    const itemName =
      (this.form.item_name || '').trim();

    const requestedBy =
      (this.form.requested_by || '').trim();

    const purpose =
      (this.form.purpose || '').trim();


    // ===================================================
    // VALIDATION
    // ===================================================

    if (!this.form.project_id) {

      this.error =
        'Please select a project.';

      return;

    }

    if (!requestedBy) {

      this.error =
        'Requested By is required.';

      return;

    }

    if (!itemName) {

      this.error =
        'Item / Material is required.';

      return;

    }

    if (
      Number(this.form.quantity) < 1
    ) {

      this.error =
        'Quantity must be at least 1.';

      return;

    }

    if (!this.form.required_date) {

      this.error =
        'Required Date is required.';

      return;

    }

    if (!purpose) {

      this.error =
        'Purpose / Requirement is required.';

      return;

    }


    // ===================================================
    // START SAVING
    // ===================================================

    this.saving = true;


    const payload = {

      project_id:
        Number(this.form.project_id),

      requested_by:
        requestedBy,

      item_name:
        itemName,

      category:
        this.form.category,

      quantity:
        Number(this.form.quantity),

      required_date:
        this.form.required_date,

      purpose:
        purpose,

      priority:
        this.form.priority,

      status:
        this.form.status,

      remarks:
        (this.form.remarks || '').trim()

    };


    const request$ =
      this.editingId !== null

        ? this.api.updateProcurementRequest(
            this.editingId,
            payload
          )

        : this.api.createProcurementRequest(
            payload
          );


    request$.subscribe({

      next: () => {

        const wasEditing =
          this.editingId !== null;

        this.saving = false;

        this.showForm = false;

        this.editingId = null;

        this.success =
          wasEditing
            ? 'Procurement request updated successfully.'
            : 'Procurement request created successfully.';

        this.loadRequests();

      },

      error: (e: any) => {

        this.saving = false;

        this.error =
          this.getErrorMessage(
            e,
            'Unable to save procurement request.'
          );

      }

    });

  }


  // =====================================================
  // DELETE
  // =====================================================

  remove(request: any): void {

    const id =
      Number(request?.id);

    if (!id) {

      this.error =
        'Invalid procurement request ID.';

      return;

    }

    const itemName =
      request?.item_name ||
      request?.item_material ||
      request?.item ||
      'this item';


    const confirmed =
      confirm(
        `Delete procurement request for "${itemName}"?`
      );


    if (!confirmed) {
      return;
    }


    this.deleting = true;

    this.error = '';
    this.success = '';


    this.api
      .deleteProcurementRequest(id)
      .subscribe({

        next: () => {

          this.deleting = false;

          this.success =
            'Procurement request deleted successfully.';

          this.loadRequests();

        },

        error: (e: any) => {

          this.deleting = false;

          this.error =
            this.getErrorMessage(
              e,
              'Unable to delete procurement request.'
            );

        }

      });

  }


  // =====================================================
  // APPROVE
  // =====================================================

  approve(request: any): void {

    const itemName =
      request?.item_name ||
      request?.item_material ||
      request?.item ||
      'this item';


    if (
      !confirm(
        `Approve procurement request for "${itemName}"?`
      )
    ) {

      return;

    }


    this.updateStatus(
      request,
      'Approved'
    );

  }


  // =====================================================
  // REJECT
  // =====================================================

  reject(request: any): void {

    const itemName =
      request?.item_name ||
      request?.item_material ||
      request?.item ||
      'this item';


    if (
      !confirm(
        `Reject procurement request for "${itemName}"?`
      )
    ) {

      return;

    }


    this.updateStatus(
      request,
      'Rejected'
    );

  }


  // =====================================================
  // UPDATE STATUS
  // =====================================================

  private updateStatus(
    request: any,
    status: string
  ): void {

    const id =
      Number(request?.id);


    if (!id) {

      this.error =
        'Invalid procurement request ID.';

      return;

    }


    const payload = {

      project_id:
        Number(
          request?.project_id
        ) || 0,

      requested_by:
        request?.requested_by || '',

      item_name:
        request?.item_name ||
        request?.item_material ||
        request?.item ||
        '',

      category:
        request?.category ||
        'Raw Materials',

      quantity:
        Number(
          request?.quantity ||
          request?.required_quantity
        ) || 1,

      required_date:
        request?.required_date || '',

      purpose:
        request?.purpose ||
        request?.requirement ||
        '',

      priority:
        request?.priority ||
        'Medium',

      status:
        status,

      remarks:
        request?.remarks ||
        ''

    };


    this.api
      .updateProcurementRequest(
        id,
        payload
      )
      .subscribe({

        next: () => {

          this.success =
            `Request ${status.toLowerCase()} successfully.`;

          this.loadRequests();

        },

        error: (e: any) => {

          this.error =
            this.getErrorMessage(
              e,
              `Unable to ${status.toLowerCase()} request.`
            );

        }

      });

  }


  // =====================================================
  // OPEN PROJECT MODAL
  // =====================================================

  openProjectModal(): void {

    this.projectForm = {

      project_name: '',

      description: '',

      status: 'Planning'

    };

    this.showProjectModal = true;

    this.error = '';
    this.success = '';

  }


  // =====================================================
  // CLOSE PROJECT MODAL
  // =====================================================

  closeProjectModal(): void {

    if (this.projectSaving) {
      return;
    }

    this.showProjectModal = false;

  }


  // =====================================================
  // SAVE NEW PROJECT
  // =====================================================

  saveProject(): void {

    this.error = '';
    this.success = '';

    const projectName =
      (this.projectForm.project_name || '').trim();


    if (!projectName) {

      this.error =
        'Project name is required.';

      return;

    }


    if (projectName.length < 2) {

      this.error =
        'Project name must contain at least 2 characters.';

      return;

    }


    this.projectSaving = true;


    const payload = {

      project_name:
        projectName,

      description:
        (
          this.projectForm.description || ''
        ).trim(),

      status:
        this.projectForm.status

    };


    this.api
      .createProject(payload)
      .subscribe({

        next: (
          createdProject: any
        ) => {

          this.projectSaving = false;

          this.showProjectModal = false;


          // ---------------------------------------------
          // Reload project list
          // ---------------------------------------------

          this.api
            .getProjects()
            .subscribe({

              next: (rows: any) => {

                this.projects =
                  Array.isArray(rows)
                    ? rows
                    : [];


                // -----------------------------------------
                // Select newly created project
                // -----------------------------------------

                const newId =
                  Number(
                    createdProject?.id ||
                    createdProject?.project_id
                  );


                if (newId) {

                  this.form.project_id =
                    newId;

                }
                else {

                  const createdName =
                    createdProject?.project_name ||
                    createdProject?.name ||
                    projectName;


                  const found =
                    this.projects.find(
                      (p: any) =>
                        (
                          p?.project_name ||
                          p?.name ||
                          ''
                        )
                          .toString()
                          .trim()
                          .toLowerCase() ===
                        createdName
                          .toString()
                          .trim()
                          .toLowerCase()
                    );


                  if (found) {

                    this.form.project_id =
                      Number(found.id);

                  }

                }


                this.success =
                  'Project created successfully.';

              },

              error: (e: any) => {

                this.loadProjects();

                this.success =
                  'Project created successfully, but project list could not be refreshed.';

                console.error(
                  'Project list refresh error:',
                  e
                );

              }

            });

        },

        error: (e: any) => {

          this.projectSaving = false;

          this.error =
            this.getErrorMessage(
              e,
              'Unable to create project.'
            );

        }

      });

  }


  // =====================================================
  // PROJECT NAME
  // =====================================================

  getProjectName(
    projectId: number
  ): string {

    const project =
      this.projects.find(
        (p: any) =>
          Number(p?.id) ===
          Number(projectId)
      );


    if (project) {

      return (
        project?.project_name ||
        project?.name ||
        `Project #${project?.id}`
      );

    }


    return `Project #${projectId}`;

  }


  // =====================================================
  // STATUS CLASS
  // =====================================================

  getStatusClass(
    status: string
  ): string {

    switch (
      (status || '')
        .toLowerCase()
        .trim()
    ) {

      case 'approved':
        return 'status-approved';

      case 'rejected':
        return 'status-rejected';

      case 'processing':
        return 'status-processing';

      case 'completed':
        return 'status-completed';

      default:
        return 'status-pending';

    }

  }


  // =====================================================
  // PRIORITY CLASS
  // =====================================================

  getPriorityClass(
    priority: string
  ): string {

    switch (
      (priority || '')
        .toLowerCase()
        .trim()
    ) {

      case 'high':
        return 'priority-high';

      case 'low':
        return 'priority-low';

      default:
        return 'priority-medium';

    }

  }


  // =====================================================
  // SUMMARY
  // =====================================================

  get totalRequests(): number {

    return this.requests.length;

  }


  get pendingRequests(): number {

    return this.requests.filter(
      (r: any) =>
        (r?.status || '')
          .toLowerCase()
          .trim() === 'pending'
    ).length;

  }


  get approvedRequests(): number {

    return this.requests.filter(
      (r: any) =>
        (r?.status || '')
          .toLowerCase()
          .trim() === 'approved'
    ).length;

  }


  get highPriorityRequests(): number {

    return this.requests.filter(
      (r: any) =>
        (r?.priority || '')
          .toLowerCase()
          .trim() === 'high'
    ).length;

  }


  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {

    this.error = '';
    this.success = '';

    this.loadRequests();
    this.loadProjects();

  }

}