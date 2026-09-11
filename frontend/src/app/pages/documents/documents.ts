import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, timeout } from 'rxjs';
import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';
@Component({selector:'app-documents',standalone:true,imports:[CommonModule,FormsModule,AppSidebarComponent],templateUrl:'./documents.html',styleUrl:'./documents.css'})
export class Documents implements OnInit{
  documents:any[]=[];projects:any[]=[];loading=false;uploading=false;actionId:number|null=null;error='';message='';role='';selectedFile:File|null=null;form:any={project_id:0,title:'',document_type:'Drawing'};
  constructor(private api:Api, private cdr:ChangeDetectorRef){try{this.role=String(JSON.parse(localStorage.getItem('currentUser')||'{}').role||'').toUpperCase()}catch{}}
  ngOnInit(){this.load()}
  canEdit(){return ['ADMIN','PROJECT_MANAGER','SITE_ENGINEER'].includes(this.role)}
  private parseError(e:any,fallback:string):string{const d=e?.error?.detail??e?.message;if(Array.isArray(d))return d.map((x:any)=>x?.msg||JSON.stringify(x)).join('\n');return typeof d==='string'?d:fallback}
  load(){
    this.loading=true;this.error='';
    forkJoin({
      documents:this.api.getDocuments().pipe(timeout(10000),catchError(()=>of([]))),
      projects:this.api.getProjects().pipe(timeout(10000),catchError(()=>of([])))
    }).pipe(finalize(()=>{this.loading=false;this.cdr.detectChanges();})).subscribe({
      next:r=>{this.documents=Array.isArray(r.documents)?r.documents:[];this.projects=Array.isArray(r.projects)?r.projects:[];if(!this.form.project_id)this.form.project_id=Number(this.projects[0]?.id||0);},
      error:e=>this.error=this.parseError(e,'Unable to load documents.')
    });
  }
  projectName(id:any){return this.projects.find(p=>Number(p.id)===Number(id))?.project_name||`Project #${id}`}
  choose(event:Event){
    const input=event.target as HTMLInputElement;
    const file=input.files?.[0]||null;
    this.error='';
    this.message='';
    if(file && file.size>15*1024*1024){
      this.selectedFile=null;
      input.value='';
      this.error='File is too large. Maximum upload size is 15 MB.';
      return;
    }
    this.selectedFile=file;
  }
  upload(){
    if(!this.canEdit())return;
    if(!this.form.project_id||!String(this.form.title||'').trim()||!this.selectedFile){this.error='Project, title and file are required.';return}
    this.uploading=true;this.error='';this.message='';
    this.api.uploadDocument(this.form.project_id,this.form.title.trim(),this.form.document_type,this.selectedFile).pipe(timeout(60000),finalize(()=>{this.uploading=false;this.cdr.detectChanges();})).subscribe({
      next:(created:any)=>{this.message='Document uploaded.';if(created?.id)this.documents=[created,...this.documents];this.form.title='';this.selectedFile=null;this.load();},
      error:e=>this.error=this.parseError(e,'Unable to upload document.')
    });
  }
  download(d:any){this.actionId=Number(d.id);this.api.downloadDocument(d.id).pipe(timeout(15000),finalize(()=>{this.actionId=null;this.cdr.detectChanges();})).subscribe({next:blob=>{const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=d.file_name||'document';a.click();URL.revokeObjectURL(url)},error:e=>this.error=this.parseError(e,'Unable to download document.')})}
  remove(d:any){if(!this.canEdit()||!confirm(`Delete ${d.title}?`))return;this.actionId=Number(d.id);this.api.deleteDocument(d.id).pipe(timeout(10000),finalize(()=>{this.actionId=null;this.cdr.detectChanges();})).subscribe({next:()=>{this.documents=this.documents.filter(x=>Number(x.id)!==Number(d.id));},error:e=>this.error=this.parseError(e,'Unable to delete document.')})}
}
