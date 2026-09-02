import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';


interface InvoiceForm {
  invoice_id: string;
  invoice_number: string;
  vendor_id: number;
  purchase_order_id: number;
  project_id: number;
  invoice_date: string;
  due_date: string;
  invoice_amount: number;
  payment_status: string;
  invoice_status: string;
  remarks: string;
}


@Component({
  selector: 'app-invoices',
  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    AppSidebarComponent
  ],

  templateUrl: './invoices.html',
  styleUrl: './invoices.css'
})
export class Invoices implements OnInit {

  // =====================================================
  // DATA
  // =====================================================

  invoices: any[] = [];

  projects: any[] = [];

  vendors: any[] = [];

  purchaseOrders: any[] = [];


  // =====================================================
  // STATES
  // =====================================================

  loading = false;

  saving = false;

  deleting = false;

  paying = false;

  loadingProjects = false;

  loadingVendors = false;

  loadingPurchaseOrders = false;


  // =====================================================
  // MESSAGES
  // =====================================================

  error = '';

  success = '';


  // =====================================================
  // FORM
  // =====================================================

  showForm = false;

  editingId: number | null = null;


  // =====================================================
  // INVOICE FORM
  // =====================================================

  form: InvoiceForm = {

    invoice_id: '',

    invoice_number: '',

    vendor_id: 0,

    purchase_order_id: 0,

    project_id: 0,

    invoice_date: '',

    due_date: '',

    invoice_amount: 0,

    payment_status: 'Pending',

    invoice_status: 'Received',

    remarks: ''

  };


  // =====================================================
  // CONSTRUCTOR
  // =====================================================

  constructor(
    private api: Api
  ) {}


  // =====================================================
  // INIT
  // =====================================================

  ngOnInit(): void {

    this.loadInvoices();

    this.loadProjects();

    this.loadVendors();

    this.loadPurchaseOrders();

  }


  // =====================================================
  // ERROR HANDLER
  // =====================================================

  private getErrorMessage(
    error: any,
    defaultMessage: string
  ): string {

    if (!error) {
      return defaultMessage;
    }


    // ---------------------------------------------------
    // FastAPI validation error
    // ---------------------------------------------------

    if (Array.isArray(error?.error?.detail)) {

      const messages =
        error.error.detail
          .map((item: any) => {

            const location =
              Array.isArray(item?.loc)
                ? item.loc
                    .filter(
                      (value: any) =>
                        value !== 'body' &&
                        value !== 'query' &&
                        value !== 'path'
                    )
                    .join(' → ')
                : '';

            const message =
              item?.msg ||
              'Invalid value';

            return location
              ? `${location}: ${message}`
              : message;

          })
          .filter(
            (message: string) =>
              message.trim() !== ''
          );

      if (messages.length > 0) {

        return messages.join('\n');

      }

    }


    // ---------------------------------------------------
    // FastAPI normal detail
    // ---------------------------------------------------

    if (
      typeof error?.error?.detail === 'string'
    ) {

      return error.error.detail;

    }


    // ---------------------------------------------------
    // Backend message
    // ---------------------------------------------------

    if (
      typeof error?.error?.message === 'string'
    ) {

      return error.error.message;

    }


    // ---------------------------------------------------
    // Network error
    // ---------------------------------------------------

    if (
      error?.status === 0
    ) {

      return (
        'Unable to connect to backend. ' +
        'Please make sure FastAPI is running on ' +
        'http://localhost:8000.'
      );

    }


    // ---------------------------------------------------
    // Angular error
    // ---------------------------------------------------

    if (
      typeof error?.message === 'string' &&
      error.message.trim() !== ''
    ) {

      return error.message;

    }


    return defaultMessage;

  }


  // =====================================================
  // LOAD INVOICES
  // =====================================================

  loadInvoices(): void {

    this.loading = true;

    this.error = '';

    this.api.getInvoices().subscribe({

      next: (rows: any) => {

        this.invoices =
          Array.isArray(rows)
            ? rows
            : [];

        this.loading = false;

      },

      error: (e: any) => {

        this.loading = false;

        this.invoices = [];

        this.error =
          this.getErrorMessage(
            e,
            'Unable to load invoices.'
          );

        console.error(
          'Load invoices error:',
          e
        );

      }

    });

  }


  // =====================================================
  // LOAD PROJECTS
  // =====================================================

  loadProjects(): void {

    this.loadingProjects = true;

    this.api.getProjects().subscribe({

      next: (rows: any) => {

        this.projects =
          Array.isArray(rows)
            ? rows
            : [];

        this.loadingProjects = false;

      },

      error: (e: any) => {

        this.projects = [];

        this.loadingProjects = false;

        console.error(
          'Load projects error:',
          e
        );

      }

    });

  }


  // =====================================================
  // LOAD VENDORS
  // =====================================================

  loadVendors(): void {

    this.loadingVendors = true;

    this.api.getVendors().subscribe({

      next: (rows: any) => {

        this.vendors =
          Array.isArray(rows)
            ? rows
            : [];

        this.loadingVendors = false;

      },

      error: (e: any) => {

        this.vendors = [];

        this.loadingVendors = false;

        console.error(
          'Load vendors error:',
          e
        );

      }

    });

  }


  // =====================================================
  // LOAD PURCHASE ORDERS
  // =====================================================

  loadPurchaseOrders(): void {

    this.loadingPurchaseOrders = true;

    this.api.getPurchaseOrders().subscribe({

      next: (rows: any) => {

        this.purchaseOrders =
          Array.isArray(rows)
            ? rows
            : [];

        this.loadingPurchaseOrders = false;

      },

      error: (e: any) => {

        this.purchaseOrders = [];

        this.loadingPurchaseOrders = false;

        console.error(
          'Load purchase orders error:',
          e
        );

      }

    });

  }


  // =====================================================
  // GENERATE INVOICE ID
  // =====================================================

  generateInvoiceId(): string {

    const now = new Date();

    const year =
      now.getFullYear();

    const month =
      String(
        now.getMonth() + 1
      ).padStart(2, '0');

    const day =
      String(
        now.getDate()
      ).padStart(2, '0');

    const timestamp =
      Date.now()
        .toString()
        .slice(-6);

    return `INV-${year}${month}${day}-${timestamp}`;

  }


  // =====================================================
  // OPEN CREATE FORM
  // =====================================================

  openCreate(): void {

    this.editingId = null;

    const today =
      new Date()
        .toISOString()
        .split('T')[0];

    this.form = {

      invoice_id:
        this.generateInvoiceId(),

      invoice_number: '',

      vendor_id:
        0,

      purchase_order_id:
        0,

      project_id:
        0,

      invoice_date:
        today,

      due_date:
        '',

      invoice_amount:
        0,

      payment_status:
        'Pending',

      invoice_status:
        'Received',

      remarks:
        ''

    };

    this.showForm = true;

    this.error = '';

    this.success = '';

  }


  // =====================================================
  // EDIT INVOICE
  // =====================================================

  edit(invoice: any): void {

    const id =
      Number(invoice?.id);

    if (!id) {

      this.error =
        'Invalid invoice ID.';

      return;

    }

    this.editingId = id;

    this.form = {

      invoice_id:
        invoice?.invoice_id ||
        this.generateInvoiceId(),

      invoice_number:
        invoice?.invoice_number ||
        '',

      vendor_id:
        Number(
          invoice?.vendor_id
        ) || 0,

      purchase_order_id:
        Number(
          invoice?.purchase_order_id
        ) || 0,

      project_id:
        Number(
          invoice?.project_id
        ) || 0,

      invoice_date:
        invoice?.invoice_date ||
        '',

      due_date:
        invoice?.due_date ||
        '',

      invoice_amount:
        Number(
          invoice?.invoice_amount
        ) || 0,

      payment_status:
        invoice?.payment_status ||
        'Pending',

      invoice_status:
        invoice?.invoice_status ||
        'Received',

      remarks:
        invoice?.remarks ||
        ''

    };

    this.showForm = true;

    this.error = '';

    this.success = '';

  }


  // =====================================================
  // CANCEL
  // =====================================================

  cancel(): void {

    if (this.saving) {
      return;
    }

    this.showForm = false;

    this.editingId = null;

    this.error = '';

    this.success = '';

  }


  // =====================================================
  // GET PURCHASE ORDER NAME
  // =====================================================

  getPurchaseOrderName(
    orderId: number
  ): string {

    const order =
      this.purchaseOrders.find(
        (item: any) =>
          Number(item?.id) ===
          Number(orderId)
      );

    if (!order) {

      return orderId
        ? `PO #${orderId}`
        : 'Not selected';

    }

    return (
      order?.purchase_order_id ||
      `PO #${order?.id}`
    );

  }


  // =====================================================
  // PURCHASE ORDER SELECTED
  // =====================================================

  onPurchaseOrderChange(): void {

    if (!this.form.purchase_order_id) {

      return;

    }

    const order =
      this.purchaseOrders.find(
        (item: any) =>
          Number(item?.id) ===
          Number(
            this.form.purchase_order_id
          )
      );

    if (!order) {

      return;

    }


    // ---------------------------------------------------
    // Automatically set project
    // ---------------------------------------------------

    if (order?.project_id) {

      this.form.project_id =
        Number(order.project_id);

    }


    // ---------------------------------------------------
    // Automatically set vendor
    // ---------------------------------------------------

    if (order?.vendor_id) {

      this.form.vendor_id =
        Number(order.vendor_id);

    }


    // ---------------------------------------------------
    // Automatically set invoice amount
    // ---------------------------------------------------

    if (
      order?.total_amount !==
      undefined &&
      order?.total_amount !== null
    ) {

      this.form.invoice_amount =
        Number(order.total_amount) || 0;

    }

  }


  // =====================================================
  // SAVE INVOICE
  // =====================================================

  save(): void {

    this.error = '';

    this.success = '';


    // ===================================================
    // VALIDATION
    // ===================================================

    if (
      !this.form.invoice_id.trim()
    ) {

      this.error =
        'Invoice ID is required.';

      return;

    }


    if (
      !this.form.invoice_number.trim()
    ) {

      this.error =
        'Invoice number is required.';

      return;

    }


    if (
      !this.form.vendor_id
    ) {

      this.error =
        'Please select a vendor.';

      return;

    }


    if (
      !this.form.purchase_order_id
    ) {

      this.error =
        'Please select a purchase order.';

      return;

    }


    if (
      !this.form.project_id
    ) {

      this.error =
        'Please select a project.';

      return;

    }


    if (
      !this.form.invoice_date
    ) {

      this.error =
        'Invoice date is required.';

      return;

    }


    if (
      !this.form.due_date
    ) {

      this.error =
        'Due date is required.';

      return;

    }


    if (
      this.form.due_date <
      this.form.invoice_date
    ) {

      this.error =
        'Due date cannot be before invoice date.';

      return;

    }


    const invoiceAmount =
      Number(
        this.form.invoice_amount
      );


    if (
      !Number.isFinite(invoiceAmount) ||
      invoiceAmount < 0
    ) {

      this.error =
        'Invoice amount must be a valid non-negative number.';

      return;

    }


    // ===================================================
    // START SAVING
    // ===================================================

    this.saving = true;


    // ===================================================
    // PAYLOAD
    // ===================================================

    const payload = {

      invoice_id:
        this.form.invoice_id.trim(),

      invoice_number:
        this.form.invoice_number.trim(),

      vendor_id:
        Number(this.form.vendor_id),

      purchase_order_id:
        Number(this.form.purchase_order_id),

      project_id:
        Number(this.form.project_id),

      invoice_date:
        this.form.invoice_date,

      due_date:
        this.form.due_date,

      invoice_amount:
        invoiceAmount,

      payment_status:
        this.form.payment_status,

      invoice_status:
        this.form.invoice_status,

      remarks:
        this.form.remarks.trim() ||
        null

    };


    // ===================================================
    // CREATE / UPDATE
    // ===================================================

    const request$ =
      this.editingId !== null

        ? this.api.updateInvoice(
            this.editingId,
            payload
          )

        : this.api.createInvoice(
            payload
          );


    request$.subscribe({

      // -------------------------------------------------
      // SUCCESS
      // -------------------------------------------------

      next: (response: any) => {

        console.log(
          'Invoice saved:',
          response
        );

        const wasEditing =
          this.editingId !== null;

        this.saving = false;

        this.showForm = false;

        this.editingId = null;

        this.success =
          wasEditing
            ? 'Invoice updated successfully.'
            : 'Invoice created successfully.';

        this.loadInvoices();

      },

      // -------------------------------------------------
      // ERROR
      // -------------------------------------------------

      error: (e: any) => {

        this.saving = false;

        console.error(
          'Invoice save error:',
          e
        );

        this.error =
          this.getErrorMessage(
            e,
            'Unable to save invoice.'
          );

      }

    });

  }


  // =====================================================
  // DELETE INVOICE
  // =====================================================

  remove(invoice: any): void {

    const id =
      Number(invoice?.id);

    if (!id) {

      this.error =
        'Invalid invoice ID.';

      return;

    }

    const invoiceNumber =
      this.getInvoiceNumber(invoice);


    const confirmed =
      confirm(
        `Delete invoice "${invoiceNumber}"?`
      );


    if (!confirmed) {

      return;

    }


    this.deleting = true;

    this.error = '';

    this.success = '';


    this.api
      .deleteInvoice(id)
      .subscribe({

        next: (response: any) => {

          console.log(
            'Invoice deleted:',
            response
          );

          this.deleting = false;

          this.success =
            'Invoice deleted successfully.';

          this.loadInvoices();

        },

        error: (e: any) => {

          this.deleting = false;

          console.error(
            'Delete invoice error:',
            e
          );

          this.error =
            this.getErrorMessage(
              e,
              'Unable to delete invoice.'
            );

        }

      });

  }


  // =====================================================
  // MARK PAID
  // =====================================================

  markPaid(invoice: any): void {

    const id =
      Number(invoice?.id);

    if (!id) {

      this.error =
        'Invalid invoice ID.';

      return;

    }


    if (
      !confirm(
        `Mark invoice ${this.getInvoiceNumber(invoice)} as paid?`
      )
    ) {

      return;

    }


    this.paying = true;

    this.error = '';

    this.success = '';


    const payload = {

      invoice_id:
        invoice?.invoice_id ||
        this.generateInvoiceId(),

      invoice_number:
        invoice?.invoice_number ||
        '',

      vendor_id:
        Number(invoice?.vendor_id) || 0,

      purchase_order_id:
        Number(
          invoice?.purchase_order_id
        ) || 0,

      project_id:
        Number(invoice?.project_id) || 0,

      invoice_date:
        invoice?.invoice_date ||
        new Date()
          .toISOString()
          .split('T')[0],

      due_date:
        invoice?.due_date ||
        new Date()
          .toISOString()
          .split('T')[0],

      invoice_amount:
        Number(
          invoice?.invoice_amount
        ) || 0,

      payment_status:
        'Paid',

      invoice_status:
        invoice?.invoice_status ||
        'Received',

      remarks:
        invoice?.remarks ||
        null

    };


    this.api
      .updateInvoice(
        id,
        payload
      )
      .subscribe({

        next: () => {

          this.paying = false;

          this.success =
            'Invoice marked as paid successfully.';

          this.loadInvoices();

        },

        error: (e: any) => {

          this.paying = false;

          console.error(
            'Mark paid error:',
            e
          );

          this.error =
            this.getErrorMessage(
              e,
              'Unable to update payment status.'
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


    return projectId
      ? `Project #${projectId}`
      : 'Not assigned';

  }


  // =====================================================
  // VENDOR NAME
  // =====================================================

  getVendorName(
    vendorId: number
  ): string {

    const vendor =
      this.vendors.find(
        (v: any) =>
          Number(v?.id) ===
          Number(vendorId)
      );


    if (vendor) {

      return (
        vendor?.vendor_name ||
        vendor?.name ||
        vendor?.company_name ||
        `Vendor #${vendor?.id}`
      );

    }


    return vendorId
      ? `Vendor #${vendorId}`
      : 'Not assigned';

  }


  // =====================================================
  // INVOICE NUMBER
  // =====================================================

  getInvoiceNumber(
    invoice: any
  ): string {

    return (
      invoice?.invoice_number ||
      invoice?.invoice_id ||
      `INV-${invoice?.id || ''}`
    );

  }


  // =====================================================
  // TOTAL AMOUNT
  // =====================================================

  getTotal(
    invoice: any
  ): number {

    return Number(
      invoice?.invoice_amount
    ) || 0;

  }


  // =====================================================
  // INVOICE STATUS CLASS
  // =====================================================

  getStatusClass(
    status: string
  ): string {

    switch (
      (status || '')
        .toLowerCase()
        .trim()
    ) {

      case 'received':
        return 'status-approved';

      case 'approved':
        return 'status-approved';

      case 'processing':
        return 'status-processing';

      case 'paid':
        return 'status-paid';

      case 'overdue':
        return 'status-overdue';

      case 'rejected':
        return 'status-rejected';

      case 'cancelled':
        return 'status-cancelled';

      case 'completed':
        return 'status-completed';

      default:
        return 'status-pending';

    }

  }


  // =====================================================
  // PAYMENT STATUS CLASS
  // =====================================================

  getPaymentStatusClass(
    status: string
  ): string {

    switch (
      (status || '')
        .toLowerCase()
        .trim()
    ) {

      case 'paid':
        return 'payment-paid';

      case 'partial':
        return 'payment-partial';

      case 'overdue':
        return 'payment-overdue';

      case 'pending':
        return 'payment-unpaid';

      default:
        return 'payment-unpaid';

    }

  }


  // =====================================================
  // SUMMARY
  // =====================================================

  get totalInvoices(): number {

    return this.invoices.length;

  }


  get paidInvoices(): number {

    return this.invoices.filter(
      (invoice: any) =>
        (
          invoice?.payment_status ||
          ''
        )
          .toLowerCase()
          .trim() === 'paid'
    ).length;

  }


  get pendingInvoices(): number {

    return this.invoices.filter(
      (invoice: any) =>
        (
          invoice?.payment_status ||
          ''
        )
          .toLowerCase()
          .trim() === 'pending'
    ).length;

  }


  get overdueInvoices(): number {

    return this.invoices.filter(
      (invoice: any) =>
        (
          invoice?.payment_status ||
          ''
        )
          .toLowerCase()
          .trim() === 'overdue'
    ).length;

  }


  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {

    this.error = '';

    this.success = '';

    this.loadInvoices();

    this.loadProjects();

    this.loadVendors();

    this.loadPurchaseOrders();

  }

}