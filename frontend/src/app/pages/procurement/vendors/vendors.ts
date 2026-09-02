import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AppSidebarComponent } from '../../../shared/app-sidebar.component';


// =====================================================
// VENDOR INTERFACE
// Backend Vendor model ke according
// =====================================================

interface Vendor {
  id: number;
  vendor_name: string;
  contact_person: string;
  contact_number: string;
  email: string;
  address: string;
  vendor_category: string;
  products_services: string;
  status: string;
}


// =====================================================
// COMPONENT
// =====================================================

@Component({
  selector: 'app-vendors',
  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    AppSidebarComponent
  ],

  templateUrl: './vendors.html',
  styleUrl: './vendors.css'
})
export class Vendors implements OnInit {

  // ===================================================
  // API URL
  // ===================================================

  private readonly apiUrl =
    'http://127.0.0.1:8000/procurement/vendors/';


  // ===================================================
  // VENDOR DATA
  // ===================================================

  vendors: Vendor[] = [];

  filteredVendors: Vendor[] = [];


  // ===================================================
  // SEARCH / FILTER
  // ===================================================

  searchText = '';

  selectedCategory = 'All';

  selectedStatus = 'All';


  // ===================================================
  // FORM
  // ===================================================

  showForm = false;

  editingId: number | null = null;


  form: Vendor = {
    id: 0,
    vendor_name: '',
    contact_person: '',
    contact_number: '',
    email: '',
    address: '',
    vendor_category: 'Raw Materials',
    products_services: '',
    status: 'Active'
  };


  // ===================================================
  // LOADING STATES
  // ===================================================

  loading = false;

  saving = false;

  deletingId: number | null = null;


  // ===================================================
  // CONSTRUCTOR
  // ===================================================

  constructor(
    private http: HttpClient
  ) {}


  // ===================================================
  // ON INIT
  // ===================================================

  ngOnInit(): void {

    this.loadVendors();

  }


  // ===================================================
  // LOAD VENDORS FROM DATABASE
  // ===================================================

  loadVendors(): void {

    this.loading = true;

    this.http.get<Vendor[]>(this.apiUrl)
      .subscribe({

        next: (data) => {

          this.vendors = Array.isArray(data)
            ? data
            : [];

          this.filterVendors();

          this.loading = false;

        },

        error: (error) => {

          console.error(
            'Error loading vendors:',
            error
          );

          this.loading = false;

          alert(
            error?.error?.detail ||
            'Unable to load vendors. Please make sure backend is running.'
          );

        }

      });

  }


  // ===================================================
  // TOTAL VENDORS
  // ===================================================

  get totalVendors(): number {

    return this.vendors.length;

  }


  // ===================================================
  // ACTIVE VENDORS
  // ===================================================

  get activeVendors(): number {

    return this.vendors.filter(
      vendor => vendor.status === 'Active'
    ).length;

  }


  // ===================================================
  // INACTIVE VENDORS
  // ===================================================

  get inactiveVendors(): number {

    return this.vendors.filter(
      vendor => vendor.status === 'Inactive'
    ).length;

  }


  // ===================================================
  // FILTER VENDORS
  // ===================================================

  filterVendors(): void {

    const search =
      this.searchText
        .toLowerCase()
        .trim();


    this.filteredVendors =
      this.vendors.filter(
        vendor => {

          const matchesSearch =
            !search ||

            vendor.vendor_name
              .toLowerCase()
              .includes(search) ||

            vendor.contact_person
              .toLowerCase()
              .includes(search) ||

            vendor.contact_number
              .toLowerCase()
              .includes(search) ||

            vendor.email
              .toLowerCase()
              .includes(search) ||

            vendor.address
              .toLowerCase()
              .includes(search) ||

            vendor.products_services
              .toLowerCase()
              .includes(search);


          const matchesCategory =
            this.selectedCategory === 'All' ||

            vendor.vendor_category ===
              this.selectedCategory;


          const matchesStatus =
            this.selectedStatus === 'All' ||

            vendor.status ===
              this.selectedStatus;


          return (
            matchesSearch &&
            matchesCategory &&
            matchesStatus
          );

        }
      );

  }


  // ===================================================
  // OPEN CREATE FORM
  // ===================================================

  openCreate(): void {

    this.editingId = null;

    this.form = {

      id: 0,

      vendor_name: '',

      contact_person: '',

      contact_number: '',

      email: '',

      address: '',

      vendor_category: 'Raw Materials',

      products_services: '',

      status: 'Active'

    };

    this.showForm = true;

  }


  // ===================================================
  // EDIT VENDOR
  // ===================================================

  editVendor(vendor: Vendor): void {

    this.editingId = vendor.id;

    this.form = {
      ...vendor
    };

    this.showForm = true;

  }


  // ===================================================
  // CREATE / UPDATE VENDOR
  // ===================================================

  saveVendor(): void {

    // -------------------------------------------------
    // VALIDATION
    // -------------------------------------------------

    if (
      !this.form.vendor_name.trim() ||
      !this.form.contact_person.trim() ||
      !this.form.contact_number.trim() ||
      !this.form.email.trim() ||
      !this.form.address.trim() ||
      !this.form.products_services.trim()
    ) {

      alert(
        'Please fill all required fields.'
      );

      return;

    }


    // -------------------------------------------------
    // EMAIL VALIDATION
    // -------------------------------------------------

    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (
      !emailPattern.test(
        this.form.email.trim()
      )
    ) {

      alert(
        'Please enter a valid email address.'
      );

      return;

    }


    // -------------------------------------------------
    // REQUEST BODY
    // id send nahi karna
    // -------------------------------------------------

    const vendorData = {

      vendor_name:
        this.form.vendor_name.trim(),

      contact_person:
        this.form.contact_person.trim(),

      contact_number:
        this.form.contact_number.trim(),

      email:
        this.form.email.trim(),

      address:
        this.form.address.trim(),

      vendor_category:
        this.form.vendor_category,

      products_services:
        this.form.products_services.trim(),

      status:
        this.form.status

    };


    this.saving = true;


    // =================================================
    // UPDATE EXISTING VENDOR
    // =================================================

    if (this.editingId !== null) {

      const url =
        `${this.apiUrl}${this.editingId}`;


      this.http.put<any>(
        url,
        vendorData
      )
      .subscribe({

        next: (response) => {

          console.log(
            'Vendor updated successfully:',
            response
          );

          this.saving = false;

          this.closeForm();

          // Database se latest data reload
          this.loadVendors();

        },

        error: (error) => {

          console.error(
            'Update vendor error:',
            error
          );

          this.saving = false;

          alert(
            error?.error?.detail ||
            'Unable to update vendor.'
          );

        }

      });

      return;

    }


    // =================================================
    // CREATE NEW VENDOR
    // =================================================

    this.http.post<any>(
      this.apiUrl,
      vendorData
    )
    .subscribe({

      next: (response) => {

        console.log(
          'Vendor created successfully:',
          response
        );

        this.saving = false;

        this.closeForm();

        // Database se latest data reload
        this.loadVendors();

      },

      error: (error) => {

        console.error(
          'Create vendor error:',
          error
        );

        this.saving = false;

        alert(
          error?.error?.detail ||
          'Unable to create vendor.'
        );

      }

    });

  }


  // ===================================================
  // DELETE VENDOR
  // ===================================================

  deleteVendor(vendor: Vendor): void {

    const confirmed =
      confirm(
        `Delete vendor "${vendor.vendor_name}"?`
      );


    if (!confirmed) {

      return;

    }


    this.deletingId = vendor.id;


    const url =
      `${this.apiUrl}${vendor.id}`;


    this.http.delete<any>(
      url
    )
    .subscribe({

      next: (response) => {

        console.log(
          'Vendor deleted successfully:',
          response
        );

        this.deletingId = null;

        // Database se latest data reload
        this.loadVendors();

      },

      error: (error) => {

        console.error(
          'Delete vendor error:',
          error
        );

        this.deletingId = null;

        alert(
          error?.error?.detail ||
          'Unable to delete vendor.'
        );

      }

    });

  }


  // ===================================================
  // TOGGLE ACTIVE / INACTIVE STATUS
  // ===================================================

  toggleStatus(vendor: Vendor): void {

    const newStatus =
      vendor.status === 'Active'
        ? 'Inactive'
        : 'Active';


    const vendorData = {

      vendor_name:
        vendor.vendor_name,

      contact_person:
        vendor.contact_person,

      contact_number:
        vendor.contact_number,

      email:
        vendor.email,

      address:
        vendor.address,

      vendor_category:
        vendor.vendor_category,

      products_services:
        vendor.products_services,

      status:
        newStatus

    };


    this.http.put<any>(
      `${this.apiUrl}${vendor.id}`,
      vendorData
    )
    .subscribe({

      next: (response) => {

        console.log(
          'Vendor status updated:',
          response
        );

        // Database se latest data reload
        this.loadVendors();

      },

      error: (error) => {

        console.error(
          'Status update error:',
          error
        );

        alert(
          error?.error?.detail ||
          'Unable to update vendor status.'
        );

      }

    });

  }


  // ===================================================
  // CLOSE FORM
  // ===================================================

  closeForm(): void {

    this.showForm = false;

    this.editingId = null;

  }


  // ===================================================
  // REFRESH
  // ===================================================

  refresh(): void {

    this.searchText = '';

    this.selectedCategory = 'All';

    this.selectedStatus = 'All';

    this.loadVendors();

  }

}