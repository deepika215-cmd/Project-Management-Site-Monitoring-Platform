import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, Observable, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({selector:'app-inventory',standalone:true,imports:[CommonModule,FormsModule,AppSidebarComponent],templateUrl:'./inventory.html',styleUrl:'./inventory.css'})
export class Inventory implements OnInit{
  materials:any[]=[];stock:any[]=[];requests:any[]=[];allocations:any[]=[];movements:any[]=[];projects:any[]=[];
  tab:'stock'|'requests'|'allocation'|'movements'='stock';
  loading=true;saving=false;actionKey='';error='';message='';today=new Date().toISOString().slice(0,10);
  categories=['Cement','Steel','Bricks','Sand','Concrete','Electrical Materials','Plumbing Materials'];
  materialForm:any={name:'',category:'Cement',unit:'bags',minimum_stock:0};
  requestForm:any={project_id:0,material_id:0,quantity:1,required_date:this.today,purpose:'',remarks:''};
  allocationForm:any={project_id:0,material_id:0,quantity:1,allocation_date:this.today,work_activity:'',responsible_user:''};
  movementForm:any={material_id:0,project_id:null,movement_type:'RECEIVED',quantity:1,remarks:''};
  constructor(private api:Api, private cdr:ChangeDetectorRef){}
  ngOnInit(){this.load()}

  private parseError(e:any,fallback:string):string{
    const detail=e?.error?.detail ?? e?.message;
    if(Array.isArray(detail)) return detail.map((x:any)=>x?.msg||JSON.stringify(x)).join('\n');
    return typeof detail==='string' ? detail : fallback;
  }
  private safe<T>(request:any, fallback:T): Observable<T>{ return request.pipe(timeout(10000), catchError(()=>of(fallback as T))); }
  private setDefaults(){
    const mat=Number(this.materials[0]?.id||0), prj=Number(this.projects[0]?.id||0);
    if(!this.requestForm.material_id)this.requestForm.material_id=mat;
    if(!this.allocationForm.material_id)this.allocationForm.material_id=mat;
    if(!this.movementForm.material_id)this.movementForm.material_id=mat;
    if(!this.requestForm.project_id)this.requestForm.project_id=prj;
    if(!this.allocationForm.project_id)this.allocationForm.project_id=prj;
  }
  load(){
    this.loading=true; this.error='';
    forkJoin({
      materials:this.safe<any[]>(this.api.getMaterials(),[]),
      stock:this.safe<any[]>(this.api.getInventoryLifecycleStatus(),[]),
      requests:this.safe<any[]>(this.api.getMaterialRequests(),[]),
      allocations:this.safe<any[]>(this.api.getMaterialAllocations(),[]),
      movements:this.safe<any[]>(this.api.getStockMovements(),[]),
      projects:this.safe<any[]>(this.api.getProjects(),[])
    }).pipe(finalize(()=>{this.loading=false;this.cdr.detectChanges();})).subscribe({
      next:r=>{this.materials=r.materials||[];this.stock=r.stock||[];this.requests=r.requests||[];this.allocations=r.allocations||[];this.movements=r.movements||[];this.projects=r.projects||[];this.setDefaults();},
      error:e=>{this.error=this.parseError(e,'Unable to load material lifecycle data.');}
    });
  }
  materialName(id:any){return this.materials.find(m=>Number(m.id)===Number(id))?.name||`Material #${id}`}
  projectName(id:any){const row=this.projects.find(p=>Number(p.id)===Number(id));return row?.project_name||row?.name||`Project #${id}`}

  createMaterial(){
    if(!String(this.materialForm.name||'').trim()){this.error='Material name is required.';return}
    this.saving=true;this.error='';this.message='';
    this.api.createMaterial({...this.materialForm,name:this.materialForm.name.trim()}).pipe(timeout(10000),finalize(()=>{this.saving=false;this.cdr.detectChanges();})).subscribe({
      next:(created:any)=>{this.message='Material created.'; if(created?.id)this.materials=[created,...this.materials]; this.materialForm={name:'',category:'Cement',unit:'bags',minimum_stock:0}; this.load();},
      error:e=>this.error=this.parseError(e,'Unable to create material.')
    });
  }
  receiveStock(){
    if(!this.movementForm.material_id||Number(this.movementForm.quantity)<=0){this.error='Select a material and quantity.';return}
    this.saving=true;this.error='';this.message='';
    this.api.createStockMovement({...this.movementForm,project_id:this.movementForm.project_id||null}).pipe(timeout(10000),finalize(()=>{this.saving=false;this.cdr.detectChanges();})).subscribe({
      next:(created:any)=>{this.message='Stock movement recorded.'; if(created?.id)this.movements=[created,...this.movements]; this.load();},
      error:e=>this.error=this.parseError(e,'Unable to record stock movement.')
    });
  }
  submitRequest(){
    if(!this.requestForm.project_id||!this.requestForm.material_id||!String(this.requestForm.purpose||'').trim()){this.error='Project, material and purpose are required.';return}
    this.saving=true;this.error='';this.message='';
    this.api.createMaterialRequest({...this.requestForm,purpose:this.requestForm.purpose.trim()}).pipe(timeout(10000),finalize(()=>{this.saving=false;this.cdr.detectChanges();})).subscribe({
      next:(created:any)=>{this.message='Material request created.'; if(created?.id)this.requests=[created,...this.requests]; this.load();},
      error:e=>this.error=this.parseError(e,'Unable to create material request.')
    });
  }
  requestAction(r:any,a:'approve'|'reject'|'fulfill'){
    const req=a==='approve'?this.api.approveMaterialRequest(r.id):a==='reject'?this.api.rejectMaterialRequest(r.id):this.api.fulfillMaterialRequest(r.id);
    this.actionKey=`request-${r.id}`;this.error='';
    req.pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({
      next:(updated:any)=>{Object.assign(r,updated||{}, {status: a==='approve'?'Approved':a==='reject'?'Rejected':'Fulfilled'}); this.load();},
      error:e=>this.error=this.parseError(e,`Unable to ${a} request.`)
    });
  }
  allocate(){
    if(!this.allocationForm.project_id||!this.allocationForm.material_id||!String(this.allocationForm.work_activity||'').trim()){this.error='Project, material and work activity are required.';return}
    this.saving=true;this.error='';this.message='';
    this.api.createMaterialAllocation({...this.allocationForm,work_activity:this.allocationForm.work_activity.trim()}).pipe(timeout(10000),finalize(()=>{this.saving=false;this.cdr.detectChanges();})).subscribe({
      next:(created:any)=>{this.message='Material allocated.'; if(created?.id)this.allocations=[created,...this.allocations]; this.load();},
      error:e=>this.error=this.parseError(e,'Unable to allocate material.')
    });
  }
  consume(a:any){
    this.actionKey=`allocation-${a.id}`;this.error='';
    this.api.consumeMaterialAllocation(a.id).pipe(timeout(10000),finalize(()=>{this.actionKey='';this.cdr.detectChanges();})).subscribe({
      next:(updated:any)=>{Object.assign(a,updated||{}, {status:'Consumed'}); this.load();},
      error:e=>this.error=this.parseError(e,'Unable to consume allocation.')
    });
  }
  total(field:string){return this.stock.reduce((s,x)=>s+Number(x[field]||0),0)}
  lowStock(){return this.stock.filter(x=>x.available_status==='LOW_STOCK'||x.available_status==='OUT_OF_STOCK').length}
}
