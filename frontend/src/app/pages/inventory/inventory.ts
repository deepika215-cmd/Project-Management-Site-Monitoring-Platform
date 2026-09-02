// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { FormsModule } from '@angular/forms';
// import { RouterLink } from '@angular/router';
// import { Api } from '../../services/api';
// import { AppSidebarComponent } from '../../shared/app-sidebar.component';

// @Component({ selector:'app-inventory', standalone:true, imports:[CommonModule,FormsModule,RouterLink,AppSidebarComponent], templateUrl:'./inventory.html', styleUrl:'./inventory.css' })
// export class Inventory implements OnInit {
//   items:any[]=[]; filtered:any[]=[]; search=''; loading=false; error='';
//   form={material_name:'',quantity:0,unit:'',supplier:'',status:'Available'}; showForm=false;
//   constructor(private api:Api){}
//   ngOnInit(){this.load();}
//   load(){this.loading=true;this.api.getInventory().subscribe({next:d=>{this.items=d||[];this.filter();this.loading=false;},error:e=>{this.loading=false;this.error=e?.error?.detail||'Unable to load inventory.';}})}
//   filter(){const s=this.search.toLowerCase().trim();this.filtered=this.items.filter(i=>!s||i.material_name.toLowerCase().includes(s)||i.supplier.toLowerCase().includes(s));}
//   availableUnits(){return this.items.reduce((sum,i)=>sum+(Number(i.quantity)||0)-(Number(i.used)||0),0);}
//   usedUnits(){return this.items.reduce((sum,i)=>sum+(Number(i.used)||0),0);}
//   add(){if(!this.form.material_name||this.form.quantity<0||!this.form.unit||!this.form.supplier)return;this.api.createInventory(this.form).subscribe({next:()=>{this.form={material_name:'',quantity:0,unit:'',supplier:'',status:'Available'};this.showForm=false;this.load();},error:e=>this.error=e?.error?.detail||'Unable to create material.'});}
//   use(item:any){const q=Number(prompt(`Quantity to use (available: ${item.quantity-item.used})`,'1'));if(!q||q<1)return;this.api.useInventory(item.id,{quantity:q}).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Unable to use stock.'});}
//   release(item:any){if(!item.used)return;const q=Number(prompt(`Quantity to release (used: ${item.used})`,'1'));if(!q||q<1)return;this.api.releaseInventory(item.id,q).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Unable to release stock.'});}
//   remove(item:any){if(!confirm(`Delete ${item.material_name}?`))return;this.api.deleteInventory(item.id).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Unable to delete material.'});}
// }


import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
  selector: 'app-inventory',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AppSidebarComponent
  ],
  templateUrl: './inventory.html',
  styleUrl: './inventory.css'
})
export class Inventory implements OnInit {

  // ============================================================
  // VARIABLES
  // ============================================================

  items: any[] = [];
  filtered: any[] = [];

  search = '';

  loading = false;
  saving = false;

  error = '';

  showForm = false;

  // ============================================================
  // FORM
  // ============================================================

  form = {
    material_name: '',
    quantity: 0,
    unit: '',
    supplier: '',
    status: 'Available'
  };


  // ============================================================
  // CONSTRUCTOR
  // ============================================================

  constructor(private api: Api) {}


  // ============================================================
  // ON INIT
  // ============================================================

  ngOnInit(): void {
    this.load();
  }


  // ============================================================
  // LOAD INVENTORY
  // ============================================================

  load(): void {

    this.loading = true;
    this.error = '';

    this.api.getInventory().subscribe({

      next: (data: any[]) => {

        this.items = data || [];

        this.filter();

        this.loading = false;
      },

      error: (e: any) => {

        console.error(
          'Inventory loading error:',
          e
        );

        this.loading = false;

        this.error =
          e?.error?.detail ||
          'Unable to load inventory.';
      }

    });
  }


  // ============================================================
  // SEARCH / FILTER
  // ============================================================

  filter(): void {

    const searchText =
      this.search
        .toLowerCase()
        .trim();

    this.filtered =
      this.items.filter((item: any) => {

        const material =
          String(
            item.material_name || ''
          ).toLowerCase();

        const supplier =
          String(
            item.supplier || ''
          ).toLowerCase();

        return (
          !searchText ||
          material.includes(searchText) ||
          supplier.includes(searchText)
        );

      });
  }


  // ============================================================
  // AVAILABLE UNITS
  // ============================================================

  availableUnits(): number {

    return this.items.reduce(
      (
        total: number,
        item: any
      ) => {

        const quantity =
          Number(item.quantity) || 0;

        const used =
          Number(item.used) || 0;

        return total + quantity - used;

      },
      0
    );
  }


  // ============================================================
  // USED UNITS
  // ============================================================

  usedUnits(): number {

    return this.items.reduce(
      (
        total: number,
        item: any
      ) => {

        return (
          total +
          (Number(item.used) || 0)
        );

      },
      0
    );
  }


  // ============================================================
  // ADD MATERIAL
  // ============================================================

  add(): void {

    this.error = '';

    const materialName =
      this.form.material_name.trim();

    const unit =
      this.form.unit.trim();

    const supplier =
      this.form.supplier.trim();

    const quantity =
      Number(this.form.quantity);


    // Validation

    if (!materialName) {

      this.error =
        'Please enter material name.';

      return;
    }


    if (
      !Number.isInteger(quantity) ||
      quantity < 0
    ) {

      this.error =
        'Please enter a valid quantity.';

      return;
    }


    if (!unit) {

      this.error =
        'Please enter unit.';

      return;
    }


    if (!supplier) {

      this.error =
        'Please enter supplier name.';

      return;
    }


    this.saving = true;


    const data = {

      material_name: materialName,

      quantity: quantity,

      unit: unit,

      supplier: supplier,

      status:
        quantity > 0
          ? 'Available'
          : 'Out of Stock'

    };


    this.api.createInventory(data)
      .subscribe({

        next: () => {

          this.form = {

            material_name: '',

            quantity: 0,

            unit: '',

            supplier: '',

            status: 'Available'

          };

          this.showForm = false;

          this.saving = false;

          this.load();

        },

        error: (e: any) => {

          console.error(
            'Create inventory error:',
            e
          );

          this.saving = false;

          this.error =
            e?.error?.detail ||
            'Unable to create material.';

        }

      });
  }


  // ============================================================
  // USE MATERIAL
  // ============================================================

  use(item: any): void {

    this.error = '';

    const quantity =
      Number(item.quantity) || 0;

    const used =
      Number(item.used) || 0;

    const available =
      quantity - used;


    if (available <= 0) {

      this.error =
        'No inventory available.';

      return;
    }


    const input =
      prompt(
        `Quantity to use (Available: ${available} ${item.unit})`,
        '1'
      );


    if (input === null) {
      return;
    }


    const useQuantity =
      Number(input);


    if (
      !Number.isInteger(useQuantity) ||
      useQuantity <= 0
    ) {

      this.error =
        'Please enter a valid quantity.';

      return;
    }


    if (useQuantity > available) {

      this.error =
        `Only ${available} ${item.unit} available.`;

      return;
    }


    this.api.useInventory(
      item.id,
      {
        quantity: useQuantity
      }
    ).subscribe({

      next: () => {

        this.error = '';

        this.load();

      },

      error: (e: any) => {

        console.error(
          'Use inventory error:',
          e
        );

        this.error =
          e?.error?.detail ||
          'Unable to use inventory.';

      }

    });
  }


  // ============================================================
  // RELEASE MATERIAL
  // ============================================================

  release(item: any): void {

    this.error = '';

    const used =
      Number(item.used) || 0;


    if (used <= 0) {

      this.error =
        'No used inventory available to release.';

      return;
    }


    const input =
      prompt(
        `Quantity to release (Used: ${used} ${item.unit})`,
        '1'
      );


    if (input === null) {
      return;
    }


    const releaseQuantity =
      Number(input);


    if (
      !Number.isInteger(releaseQuantity) ||
      releaseQuantity <= 0
    ) {

      this.error =
        'Please enter a valid quantity.';

      return;
    }


    if (releaseQuantity > used) {

      this.error =
        `Only ${used} ${item.unit} is currently used.`;

      return;
    }


    // IMPORTANT:
    // API expects:
    // {
    //    quantity: number
    // }

    this.api.releaseInventory(
  item.id,
  releaseQuantity
).subscribe({

  next: () => {
    this.error = '';
    this.load();
  },

  error: (e: any) => {
    console.error(
      'Release inventory error:',
      e
    );

    this.error =
      e?.error?.detail ||
      'Unable to release inventory.';
  }

});
  }


  // ============================================================
  // DELETE MATERIAL
  // ============================================================

  remove(item: any): void {

    this.error = '';

    const confirmed =
      confirm(
        `Are you sure you want to delete "${item.material_name}"?`
      );


    if (!confirmed) {
      return;
    }


    this.api
      .deleteInventory(item.id)
      .subscribe({

        next: () => {

          this.error = '';

          this.load();

        },

        error: (e: any) => {

          console.error(
            'Delete inventory error:',
            e
          );

          this.error =
            e?.error?.detail ||
            'Unable to delete material.';

        }

      });
  }


  // ============================================================
  // GET AVAILABLE QUANTITY
  // ============================================================

  getAvailable(item: any): number {

    return (
      (Number(item.quantity) || 0) -
      (Number(item.used) || 0)
    );
  }


  // ============================================================
  // CHECK OUT OF STOCK
  // ============================================================

  isOutOfStock(item: any): boolean {

    return this.getAvailable(item) <= 0;
  }

}