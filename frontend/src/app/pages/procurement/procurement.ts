import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, Observable, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({selector:'app-procurement',standalone:true,imports:[CommonModule,FormsModule,AppSidebarComponent],templateUrl:'./procurement.html',styleUrl:'./procurement.css'})
export class Procurement implements OnInit{
  tab:'requests'|'vendors'|'orders'|'invoices'='requests';requests:any[]=[];vendors:any[]=[];orders:any[]=[];orderItems:any[]=[];invoices:any[]=[];projects:any[]=[];
  loading=true;saving=false;actionKey='';error='';message='';today=new Date().toISOString().slice(0,10);role='';userId=0;
  categories=['Raw Materials','Equipment','Machinery','Safety Equipment','Office Supplies'];
  requestForm:any={project_id:0,requested_by:0,item_name:'',category:'Raw Materials',quantity:1,required_date:this.today,purpose:'',priority:'NORMAL',request_date:this.today,remarks:''};
  vendorForm:any={vendor_name:'',contact_person:'',contact_number:'',email:'',address:'',category:'Raw Materials',products_services:'',status:'ACTIVE'};
  orderForm:any={vendor_id:0,project_id:0,procurement_request_id:0,order_date:this.today,expected_delivery_date:null,total_amount:0,tax_amount:0,additional_charges:0,overall_amount:0,status:'Processing'};
  itemForm:any={purchase_order_id:0,item_name:'',category:'Raw Materials',quantity:1,unit_price:0};
  invoiceForm:any={invoice_number:'',vendor_id:0,purchase_order_id:0,project_id:0,invoice_date:this.today,due_date:null,invoice_amount:0,payment_status:'Pending',invoice_status:'Received',remarks:''};
  constructor(private api:Api, private cdr:ChangeDetectorRef){try{const u=JSON.parse(localStorage.getItem('currentUser')||'{}');this.role=String(u.role||'').toUpperCase();this.userId=Number(u.id||0)}catch{}}
  ngOnInit(){this.load()}

  private parseError(e:any,fallback:string):string{const d=e?.error?.detail??e?.message;if(Array.isArray(d))return d.map((x:any)=>x?.msg||JSON.stringify(x)).join('\n');return typeof d==='string'?d:fallback}
  private safe<T>(req:any,fallback:T): Observable<T>{return req.pipe(timeout(10000),catchError(()=>of(fallback as T)))}
  load(){
    this.loading=true;this.error='';
    forkJoin({
      requests:this.safe<any[]>(this.api.getProcurementRequests(),[]),
      vendors:this.safe<any[]>(this.api.getVendors(),[]),
      orders:this.safe<any[]>(this.api.getPurchaseOrders(),[]),
      orderItems:this.safe<any[]>(this.api.getPurchaseOrderItems(),[]),
      invoices:this.safe<any[]>(this.api.getInvoices(),[]),
      projects:this.safe<any[]>(this.api.getProjects(),[])
    }).pipe(finalize(()=>{this.loading=false;this.cdr.detectChanges();})).subscribe({
      next:r=>{this.requests=r.requests||[];this.vendors=r.vendors||[];this.orders=r.orders||[];this.orderItems=r.orderItems||[];this.invoices=r.invoices||[];this.projects=r.projects||[];this.applyDefaults();},
      error:e=>this.error=this.parseError(e,'Unable to load procurement workflow.')
    });
  }
  private applyDefaults(){
    const p=Number(this.projects[0]?.id||0),v=Number(this.vendors[0]?.id||0),rq=Number(this.approvedRequests()[0]?.id||0),po=Number(this.orders[0]?.id||0);
    Object.assign(this.requestForm,{project_id:this.requestForm.project_id||p,requested_by:this.userId});
    Object.assign(this.orderForm,{project_id:this.orderForm.project_id||p,vendor_id:this.orderForm.vendor_id||v,procurement_request_id:this.orderForm.procurement_request_id||rq});
    Object.assign(this.invoiceForm,{project_id:this.invoiceForm.project_id||p,vendor_id:this.invoiceForm.vendor_id||v,purchase_order_id:this.invoiceForm.purchase_order_id||po});
    this.itemForm.purchase_order_id=this.itemForm.purchase_order_id||po;
  }
  canApprove(){return this.role==='ADMIN'||this.role==='PROJECT_MANAGER'}
  canDelete(){return this.role==='ADMIN'}
  project(id:any){return this.projects.find(p=>Number(p.id)===Number(id))?.project_name||`Project #${id}`}
  vendor(id:any){return this.vendors.find(v=>Number(v.id)===Number(id))?.vendor_name||`Vendor #${id}`}
  approvedRequests(){return this.requests.filter(r=>String(r.status).toLowerCase()==='approved')}
  private runSave(req:any,success:string,after:(x:any)=>void,fallback:string){this.saving=true;this.error='';this.message='';req.pipe(timeout(10000),finalize(()=>{this.saving=false;this.cdr.detectChanges();})).subscribe({next:(x:any)=>{this.message=success;after(x);this.load();},error:(e:any)=>this.error=this.parseError(e,fallback)})}
  createRequest(){
    if(!this.requestForm.project_id||!String(this.requestForm.item_name||'').trim()||!String(this.requestForm.purpose||'').trim()){this.error='Project, item and purpose are required.';return}
    if(!this.userId){this.error='Current user ID is unavailable. Log in again before creating a request.';return}
    this.runSave(this.api.createProcurementRequest({...this.requestForm,item_name:this.requestForm.item_name.trim(),purpose:this.requestForm.purpose.trim(),requested_by:this.userId}),'Procurement request created.',(x:any)=>{if(x?.id)this.requests=[x,...this.requests]},'Unable to create procurement request.');
  }
  requestAction(r:any,a:'approve'|'reject'){
    const x=a==='approve'?this.api.approveProcurementRequest(r.id):this.api.rejectProcurementRequest(r.id);
    this.actionKey=`request-${r.id}`;this.error='';
    x.pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({next:u=>{Object.assign(r,u||{}, {status:a==='approve'?'Approved':'Rejected'});this.load();},error:e=>this.error=this.parseError(e,`Unable to ${a} request.`)});
  }
  createVendor(){if(!String(this.vendorForm.vendor_name||'').trim()){this.error='Vendor name is required.';return}this.runSave(this.api.createVendor({...this.vendorForm,vendor_name:this.vendorForm.vendor_name.trim()}),'Vendor created.',(x:any)=>{if(x?.id)this.vendors=[x,...this.vendors];this.vendorForm={vendor_name:'',contact_person:'',contact_number:'',email:'',address:'',category:'Raw Materials',products_services:'',status:'ACTIVE'}},'Unable to create vendor.')}
  createOrder(){const f={...this.orderForm};f.overall_amount=Number(f.total_amount||0)+Number(f.tax_amount||0)+Number(f.additional_charges||0);if(!f.vendor_id||!f.project_id||!f.procurement_request_id){this.error='Vendor, project and approved procurement request are required.';return}this.runSave(this.api.createPurchaseOrder({...f,expected_delivery_date:f.expected_delivery_date||null}),'Purchase order created.',(x:any)=>{if(x?.id)this.orders=[x,...this.orders]},'Unable to create purchase order.')}
  orderItemsFor(id:any){return this.orderItems.filter(x=>Number(x.purchase_order_id)===Number(id))}
  createOrderItem(){const f={...this.itemForm};if(!f.purchase_order_id||!String(f.item_name||'').trim()||Number(f.quantity)<=0||Number(f.unit_price)<0){this.error='Purchase order, item, quantity and unit price are required.';return}this.runSave(this.api.createPurchaseOrderItem({...f,item_name:f.item_name.trim()}),'Purchase order item added.',(x:any)=>{if(x?.id)this.orderItems=[x,...this.orderItems];this.itemForm={...this.itemForm,item_name:'',quantity:1,unit_price:0}},'Unable to add purchase order item.')}
  removeOrderItem(id:number){if(!confirm('Delete this purchase order item?'))return;this.actionKey=`item-${id}`;this.api.deletePurchaseOrderItem(id).pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({next:()=>{this.orderItems=this.orderItems.filter(x=>Number(x.id)!==Number(id));},error:e=>this.error=this.parseError(e,'Unable to delete item.')})}
  private orderAction(o:any,name:'receive'|'complete'){const req=name==='receive'?this.api.receivePurchaseOrder(o.id):this.api.completePurchaseOrder(o.id);this.actionKey=`order-${o.id}`;req.pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({next:x=>{Object.assign(o,x||{});this.load();},error:e=>this.error=this.parseError(e,`Unable to ${name} purchase order.`)})}
  receiveOrder(o:any){this.orderAction(o,'receive')}
  completeOrder(o:any){this.orderAction(o,'complete')}
  createInvoice(){const f={...this.invoiceForm};if(!String(f.invoice_number||'').trim()||!f.vendor_id||!f.purchase_order_id||!f.project_id||Number(f.invoice_amount)<=0){this.error='Invoice number, vendor, purchase order, project and amount are required.';return}this.runSave(this.api.createInvoice({...f,invoice_number:f.invoice_number.trim(),due_date:f.due_date||null}),'Invoice created.',(x:any)=>{if(x?.id)this.invoices=[x,...this.invoices]},'Unable to create invoice.')}
  invoiceStatus(i:any,s:string){this.actionKey=`invoice-${i.id}`;this.api.updateInvoiceStatus(i.id,s).pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({next:x=>{Object.assign(i,x||{}, {invoice_status:s});},error:e=>this.error=this.parseError(e,'Unable to update invoice status.')})}
  paymentStatus(i:any,s:string){this.actionKey=`invoice-${i.id}`;this.api.updateInvoicePaymentStatus(i.id,s).pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({next:x=>{Object.assign(i,x||{}, {payment_status:s});},error:e=>this.error=this.parseError(e,'Unable to update payment status.')})}
  pending(){return this.requests.filter(r=>r.status==='Pending').length}
  overdue(){return this.invoices.filter(i=>i.payment_status==='Overdue').length}
}
