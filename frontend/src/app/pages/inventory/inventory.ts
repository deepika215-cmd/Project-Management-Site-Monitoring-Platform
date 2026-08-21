import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Api } from '../../services/api';

@Component({ selector:'app-inventory', standalone:true, imports:[CommonModule,FormsModule,RouterLink], templateUrl:'./inventory.html', styleUrl:'./inventory.css' })
export class Inventory implements OnInit {
  items:any[]=[]; filtered:any[]=[]; search=''; loading=false; error='';
  form={material_name:'',quantity:0,unit:'',supplier:'',status:'Available'}; showForm=false;
  constructor(private api:Api){}
  ngOnInit(){this.load();}
  load(){this.loading=true;this.api.getInventory().subscribe({next:d=>{this.items=d||[];this.filter();this.loading=false;},error:e=>{this.loading=false;this.error=e?.error?.detail||'Unable to load inventory.';}})}
  filter(){const s=this.search.toLowerCase().trim();this.filtered=this.items.filter(i=>!s||i.material_name.toLowerCase().includes(s)||i.supplier.toLowerCase().includes(s));}
  availableUnits(){return this.items.reduce((sum,i)=>sum+(Number(i.quantity)||0)-(Number(i.used)||0),0);}
  usedUnits(){return this.items.reduce((sum,i)=>sum+(Number(i.used)||0),0);}
  add(){if(!this.form.material_name||this.form.quantity<0||!this.form.unit||!this.form.supplier)return;this.api.createInventory(this.form).subscribe({next:()=>{this.form={material_name:'',quantity:0,unit:'',supplier:'',status:'Available'};this.showForm=false;this.load();},error:e=>this.error=e?.error?.detail||'Unable to create material.'});}
  use(item:any){const q=Number(prompt(`Quantity to use (available: ${item.quantity-item.used})`,'1'));if(!q||q<1)return;this.api.useInventory(item.id,{quantity:q}).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Unable to use stock.'});}
  release(item:any){if(!item.used)return;const q=Number(prompt(`Quantity to release (used: ${item.used})`,'1'));if(!q||q<1)return;this.api.releaseInventory(item.id,q).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Unable to release stock.'});}
  remove(item:any){if(!confirm(`Delete ${item.material_name}?`))return;this.api.deleteInventory(item.id).subscribe({next:()=>this.load(),error:e=>this.error=e?.error?.detail||'Unable to delete material.'});}
}
