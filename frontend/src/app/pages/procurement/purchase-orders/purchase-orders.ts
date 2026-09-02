import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api } from '../../../services/api';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';

interface PurchaseOrderForm {
  purchase_order_id: string;
  vendor_id: number;
  project_id: number;
  procurement_request_id: number;
  order_date: string;
  expected_delivery_date: string;
  quantity: number;
  unit_price: number;
  taxes: number;
  additional_charges: number;
  total_amount: number;
  status: string;
  remarks: string;
}

@Component({
  selector: 'app-purchase-orders',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AppSidebarComponent
  ],
  templateUrl: './purchase-orders.html',
  styleUrl: './purchase-orders.css'
})
export class PurchaseOrders implements OnInit {

  // =====================================================
  // DATA
  // =====================================================

  orders: any[] = [];
  projects: any[] = [];
  vendors: any[] = [];
  procurementRequests: any[] = [];


  // =====================================================
  // STATES
  // =====================================================

  loading = false;
  saving = false;
  deleting = false;
  loadingProjects = false;
  loadingVendors = false;
  loadingRequests = false;


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
  // PURCHASE ORDER FORM
  // =====================================================

  form: PurchaseOrderForm = {
    purchase_order_id: '',
    vendor_id: 0,
    project_id: 0,
    procurement_request_id: 0,
    order_date: '',
    expected_delivery_date: '',
    quantity: 1,
    unit_price: 0,
    taxes: 0,
    additional_charges: 0,
    total_amount: 0,
    status: 'Processing',
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

    this.loadOrders();
    this.loadProjects();
    this.loadVendors();
    this.loadProcurementRequests();

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


    // FastAPI validation error
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


    // FastAPI detail
    if (
      typeof error?.error?.detail === 'string'
    ) {
      return error.error.detail;
    }


    // Backend message
    if (
      typeof error?.error?.message === 'string'
    ) {
      return error.error.message;
    }


    // Network error
    if (error?.status === 0) {

      return (
        'Unable to connect to backend. ' +
        'Please make sure FastAPI is running on ' +
        'http://localhost:8000.'
      );
    }


    // Angular message
    if (
      typeof error?.message === 'string' &&
      error.message.trim() !== ''
    ) {
      return error.message;
    }


    return defaultMessage;
  }


  // =====================================================
  // GENERATE PURCHASE ORDER ID
  // =====================================================

  generatePurchaseOrderId(): string {

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

    const random =
      Math.floor(
        1000 + Math.random() * 9000
      );

    return `PO-${year}${month}${day}-${random}`;
  }


  // =====================================================
  // LOAD PURCHASE ORDERS
  // =====================================================

  loadOrders(): void {

    this.loading = true;
    this.error = '';

    this.api.getPurchaseOrders().subscribe({

      next: (rows: any) => {

        this.orders =
          Array.isArray(rows)
            ? rows
            : [];

        this.loading = false;

      },

      error: (e: any) => {

        this.loading = false;
        this.orders = [];

        this.error =
          this.getErrorMessage(
            e,
            'Unable to load purchase orders.'
          );

        console.error(
          'Load purchase orders error:',
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
  // LOAD PROCUREMENT REQUESTS
  // =====================================================

  loadProcurementRequests(): void {

    this.loadingRequests = true;

    this.api.getProcurementRequests().subscribe({

      next: (rows: any) => {

        this.procurementRequests =
          Array.isArray(rows)
            ? rows
            : [];

        this.loadingRequests = false;

      },

      error: (e: any) => {

        this.procurementRequests = [];
        this.loadingRequests = false;

        console.error(
          'Load procurement requests error:',
          e
        );

      }

    });

  }


  // =====================================================
  // OPEN CREATE
  // =====================================================

  openCreate(): void {

    this.editingId = null;

    const today =
      new Date()
        .toISOString()
        .split('T')[0];

    this.form = {

      purchase_order_id:
        this.generatePurchaseOrderId(),

      vendor_id:
        0,

      project_id:
        0,

      procurement_request_id:
        0,

      order_date:
        today,

      expected_delivery_date:
        '',

      quantity:
        1,

      unit_price:
        0,

      taxes:
        0,

      additional_charges:
        0,

      total_amount:
        0,

      status:
        'Processing',

      remarks:
        ''

    };

    this.showForm = true;

    this.error = '';
    this.success = '';

  }


  // =====================================================
  // EDIT
  // =====================================================

  edit(order: any): void {

    const id =
      Number(order?.id);

    if (!id) {

      this.error =
        'Invalid purchase order ID.';

      return;

    }


    this.editingId = id;

    this.form = {

      purchase_order_id:
        order?.purchase_order_id ||
        this.generatePurchaseOrderId(),

      vendor_id:
        Number(
          order?.vendor_id
        ) || 0,

      project_id:
        Number(
          order?.project_id
        ) || 0,

      procurement_request_id:
        Number(
          order?.procurement_request_id
        ) || 0,

      order_date:
        order?.order_date ||
        '',

      expected_delivery_date:
        order?.expected_delivery_date ||
        '',

      quantity:
        Number(
          order?.quantity
        ) || 1,

      unit_price:
        Number(
          order?.unit_price
        ) || 0,

      taxes:
        Number(
          order?.taxes
        ) || 0,

      additional_charges:
        Number(
          order?.additional_charges
        ) || 0,

      total_amount:
        Number(
          order?.total_amount
        ) || 0,

      status:
        order?.status ||
        'Processing',

      remarks:
        order?.remarks ||
        ''

    };

    this.showForm = true;

    this.error = '';
    this.success = '';

  }


  // =====================================================
  // PROCUREMENT REQUEST CHANGE
  // =====================================================

  onProcurementRequestChange(): void {

    const requestId =
      Number(
        this.form.procurement_request_id
      );

    if (!requestId) {
      return;
    }


    const request =
      this.procurementRequests.find(
        (item: any) =>
          Number(item?.id) ===
          requestId
      );

    if (!request) {
      return;
    }


    // Set project
    if (request?.project_id) {

      this.form.project_id =
        Number(request.project_id);

    }


    // Set quantity
    if (request?.quantity) {

      this.form.quantity =
        Number(request.quantity);

    }


    this.calculateTotal();

  }


  // =====================================================
  // CALCULATE TOTAL
  // =====================================================

  calculateTotal(): void {

    const quantity =
      Number(this.form.quantity) || 0;

    const unitPrice =
      Number(this.form.unit_price) || 0;

    const taxes =
      Number(this.form.taxes) || 0;

    const additionalCharges =
      Number(
        this.form.additional_charges
      ) || 0;

    this.form.total_amount =
      (quantity * unitPrice) +
      taxes +
      additionalCharges;

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
  // SAVE PURCHASE ORDER
  // =====================================================

  save(): void {

    this.error = '';
    this.success = '';


    // ---------------------------------------------------
    // Purchase Order ID
    // ---------------------------------------------------

    if (
      !this.form.purchase_order_id.trim()
    ) {

      this.error =
        'Purchase Order ID is required.';

      return;

    }


    // ---------------------------------------------------
    // Vendor
    // ---------------------------------------------------

    if (!this.form.vendor_id) {

      this.error =
        'Please select a vendor.';

      return;

    }


    // ---------------------------------------------------
    // Project
    // ---------------------------------------------------

    if (!this.form.project_id) {

      this.error =
        'Please select a project.';

      return;

    }


    // ---------------------------------------------------
    // Procurement Request
    // ---------------------------------------------------

    if (
      !this.form.procurement_request_id
    ) {

      this.error =
        'Please select a procurement request.';

      return;

    }


    // ---------------------------------------------------
    // Order Date
    // ---------------------------------------------------

    if (!this.form.order_date) {

      this.error =
        'Order date is required.';

      return;

    }


    // ---------------------------------------------------
    // Delivery Date
    // ---------------------------------------------------

    if (
      !this.form.expected_delivery_date
    ) {

      this.error =
        'Expected delivery date is required.';

      return;

    }


    // ---------------------------------------------------
    // Date validation
    // ---------------------------------------------------

    if (
      this.form.expected_delivery_date <
      this.form.order_date
    ) {

      this.error =
        'Expected delivery date cannot be before order date.';

      return;

    }


    // ---------------------------------------------------
    // Quantity
    // ---------------------------------------------------

    const quantity =
      Number(this.form.quantity);

    if (
      !Number.isFinite(quantity) ||
      quantity < 1
    ) {

      this.error =
        'Quantity must be at least 1.';

      return;

    }


    // ---------------------------------------------------
    // Unit Price
    // ---------------------------------------------------

    const unitPrice =
      Number(this.form.unit_price);

    if (
      !Number.isFinite(unitPrice) ||
      unitPrice < 0
    ) {

      this.error =
        'Unit price must be a valid non-negative number.';

      return;

    }


    // ---------------------------------------------------
    // Taxes
    // ---------------------------------------------------

    const taxes =
      Number(this.form.taxes);

    if (
      !Number.isFinite(taxes) ||
      taxes < 0
    ) {

      this.error =
        'Taxes must be a valid non-negative number.';

      return;

    }


    // ---------------------------------------------------
    // Additional Charges
    // ---------------------------------------------------

    const additionalCharges =
      Number(
        this.form.additional_charges
      );

    if (
      !Number.isFinite(additionalCharges) ||
      additionalCharges < 0
    ) {

      this.error =
        'Additional charges must be a valid non-negative number.';

      return;

    }


    // ---------------------------------------------------
    // Calculate total
    // ---------------------------------------------------

    const totalAmount =
      (
        quantity * unitPrice
      ) +
      taxes +
      additionalCharges;


    this.form.total_amount =
      totalAmount;


    // ---------------------------------------------------
    // START SAVE
    // ---------------------------------------------------

    this.saving = true;


    // ===================================================
    // EXACT BACKEND PAYLOAD
    // ===================================================

    const payload = {

      purchase_order_id:
        this.form.purchase_order_id.trim(),

      vendor_id:
        Number(this.form.vendor_id),

      project_id:
        Number(this.form.project_id),

      procurement_request_id:
        Number(
          this.form.procurement_request_id
        ),

      order_date:
        this.form.order_date,

      expected_delivery_date:
        this.form.expected_delivery_date,

      quantity:
        quantity,

      unit_price:
        unitPrice,

      taxes:
        taxes,

      additional_charges:
        additionalCharges,

      total_amount:
        totalAmount,

      status:
        this.form.status,

      remarks:
        this.form.remarks.trim() ||
        null

    };


    // ===================================================
    // CREATE / UPDATE
    // ===================================================

    const request$ =
      this.editingId !== null

        ? this.api.updatePurchaseOrder(
            this.editingId,
            payload
          )

        : this.api.createPurchaseOrder(
            payload
          );


    request$.subscribe({

      // -------------------------------------------------
      // SUCCESS
      // -------------------------------------------------

      next: (response: any) => {

        console.log(
          'Purchase order saved:',
          response
        );

        const wasEditing =
          this.editingId !== null;

        this.saving = false;

        this.showForm = false;

        this.editingId = null;

        this.success =
          wasEditing
            ? 'Purchase order updated successfully.'
            : 'Purchase order created successfully.';

        this.loadOrders();

      },


      // -------------------------------------------------
      // ERROR
      // -------------------------------------------------

      error: (e: any) => {

        this.saving = false;

        console.error(
          'Purchase order save error:',
          e
        );

        this.error =
          this.getErrorMessage(
            e,
            'Unable to save purchase order.'
          );

      }

    });

  }


  // =====================================================
  // DELETE
  // =====================================================

  remove(order: any): void {

    const id =
      Number(order?.id);

    if (!id) {

      this.error =
        'Invalid purchase order ID.';

      return;

    }


    const purchaseOrderId =
      order?.purchase_order_id ||
      `PO #${id}`;


    if (
      !confirm(
        `Delete purchase order "${purchaseOrderId}"?`
      )
    ) {

      return;

    }


    this.deleting = true;

    this.error = '';
    this.success = '';


    this.api
      .deletePurchaseOrder(id)
      .subscribe({

        next: (response: any) => {

          console.log(
            'Purchase order deleted:',
            response
          );

          this.deleting = false;

          this.success =
            'Purchase order deleted successfully.';

          this.loadOrders();

        },

        error: (e: any) => {

          this.deleting = false;

          console.error(
            'Delete purchase order error:',
            e
          );

          this.error =
            this.getErrorMessage(
              e,
              'Unable to delete purchase order.'
            );

        }

      });

  }


  // =====================================================
  // APPROVE
  // =====================================================

  approve(order: any): void {

    const id =
      Number(order?.id);

    if (!id) {

      this.error =
        'Invalid purchase order ID.';

      return;

    }


    if (
      !confirm(
        `Approve purchase order "${order?.purchase_order_id || id}"?`
      )
    ) {

      return;

    }


    this.updateStatus(
      order,
      'Approved'
    );

  }


  // =====================================================
  // REJECT
  // =====================================================

  reject(order: any): void {

    const id =
      Number(order?.id);

    if (!id) {

      this.error =
        'Invalid purchase order ID.';

      return;

    }


    if (
      !confirm(
        `Reject purchase order "${order?.purchase_order_id || id}"?`
      )
    ) {

      return;

    }


    this.updateStatus(
      order,
      'Rejected'
    );

  }


  // =====================================================
  // UPDATE STATUS
  // =====================================================

  private updateStatus(
    order: any,
    status: string
  ): void {

    const id =
      Number(order?.id);

    if (!id) {

      this.error =
        'Invalid purchase order ID.';

      return;

    }


    const quantity =
      Number(order?.quantity) || 1;

    const unitPrice =
      Number(order?.unit_price) || 0;

    const taxes =
      Number(order?.taxes) || 0;

    const additionalCharges =
      Number(
        order?.additional_charges
      ) || 0;

    const totalAmount =
      Number(
        order?.total_amount
      ) ||
      (
        quantity * unitPrice
      ) +
      taxes +
      additionalCharges;


    const payload = {

      purchase_order_id:
        order?.purchase_order_id ||
        this.generatePurchaseOrderId(),

      vendor_id:
        Number(order?.vendor_id) || 0,

      project_id:
        Number(order?.project_id) || 0,

      procurement_request_id:
        Number(
          order?.procurement_request_id
        ) || 0,

      order_date:
        order?.order_date ||
        new Date()
          .toISOString()
          .split('T')[0],

      expected_delivery_date:
        order?.expected_delivery_date ||
        order?.delivery_date ||
        new Date()
          .toISOString()
          .split('T')[0],

      quantity:
        quantity,

      unit_price:
        unitPrice,

      taxes:
        taxes,

      additional_charges:
        additionalCharges,

      total_amount:
        totalAmount,

      status:
        status,

      remarks:
        order?.remarks ||
        null

    };


    this.api
      .updatePurchaseOrder(
        id,
        payload
      )
      .subscribe({

        next: () => {

          this.success =
            `Purchase order ${status.toLowerCase()} successfully.`;

          this.loadOrders();

        },

        error: (e: any) => {

          console.error(
            'Purchase order status error:',
            e
          );

          this.error =
            this.getErrorMessage(
              e,
              `Unable to ${status.toLowerCase()} purchase order.`
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
  // PROCUREMENT REQUEST ID
  // =====================================================

  getProcurementRequestId(
    requestId: number
  ): string {

    const request =
      this.procurementRequests.find(
        (item: any) =>
          Number(item?.id) ===
          Number(requestId)
      );


    if (request) {

      return (
        request?.request_id ||
        `Request #${request?.id}`
      );

    }


    return requestId
      ? `Request #${requestId}`
      : 'Not assigned';

  }


  // =====================================================
  // TOTAL
  // =====================================================

  getTotal(
    order: any
  ): number {

    return (
      Number(order?.total_amount) ||
      (
        (
          Number(order?.quantity) || 0
        ) *
        (
          Number(order?.unit_price) || 0
        )
      ) +
      (
        Number(order?.taxes) || 0
      ) +
      (
        Number(order?.additional_charges) || 0
      )
    );

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

      case 'cancelled':
        return 'status-cancelled';

      default:
        return 'status-pending';

    }

  }


  // =====================================================
  // SUMMARY
  // =====================================================

  get totalOrders(): number {

    return this.orders.length;

  }


  get processingOrders(): number {

    return this.orders.filter(
      (order: any) =>
        (
          order?.status ||
          ''
        )
          .toLowerCase() ===
        'processing'
    ).length;

  }


  get approvedOrders(): number {

    return this.orders.filter(
      (order: any) =>
        (
          order?.status ||
          ''
        )
          .toLowerCase() ===
        'approved'
    ).length;

  }


  get completedOrders(): number {

    return this.orders.filter(
      (order: any) =>
        (
          order?.status ||
          ''
        )
          .toLowerCase() ===
        'completed'
    ).length;

  }


  // =====================================================
  // REFRESH
  // =====================================================

  refresh(): void {

    this.error = '';
    this.success = '';

    this.loadOrders();
    this.loadProjects();
    this.loadVendors();
    this.loadProcurementRequests();

  }

}