from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.project import Project
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.core.permissions import role_required

router=APIRouter(prefix='/expenses',tags=['Expenses'])
READ=role_required(['ADMIN','PROJECT_MANAGER','SITE_ENGINEER','CLIENT'])
EDIT=role_required(['ADMIN','PROJECT_MANAGER'])

def _key(v): return str(v or '').strip().upper().replace(' COST','').replace(' ','_')
def _category(db,name=None,cid=None):
    if cid:
        row=db.query(BudgetCategory).filter(BudgetCategory.id==cid).first()
        if not row: raise HTTPException(404,'Budget category not found')
        return row
    key=_key(name)
    if not key:return None
    labels={'LABOR':'Labor Cost','MATERIAL':'Material Cost','EQUIPMENT':'Equipment Cost','TRANSPORTATION':'Transportation Cost','MAINTENANCE':'Maintenance Cost','ADMINISTRATIVE':'Administrative Cost'}
    label=labels.get(key,str(name).replace('_',' ').title())
    row=db.query(BudgetCategory).filter(func.upper(BudgetCategory.name)==label.upper()).first()
    if not row:row=BudgetCategory(name=label);db.add(row);db.flush()
    return row

def _serialize(x):
    cat=x.category.name if x.category else None
    return {'id':x.id,'project_id':x.project_id,'budget_id':x.budget_id,'category_id':x.category_id,'category':_key(cat),'category_name':cat,'expense_name':x.expense_name,'amount':x.amount,'description':x.description,'expense_date':x.expense_date,'payment_status':x.payment_status,'supplier':x.supplier,'reference':x.reference,'source_module':x.source_module or 'MANUAL'}

@router.post('/')
def create(data:ExpenseCreate,db:Session=Depends(get_db),_=Depends(EDIT)):
    if not db.query(Project).filter(Project.id==data.project_id).first():raise HTTPException(404,'Project not found')
    if data.budget_id:
        b=db.query(Budget).filter(Budget.id==data.budget_id).first()
        if not b or b.project_id!=data.project_id:raise HTTPException(400,'Budget does not belong to this project')
    cat=_category(db,data.category,data.category_id)
    name=(data.expense_name or data.description or 'Project Expense').strip()
    row=Expense(project_id=data.project_id,budget_id=data.budget_id,category_id=cat.id if cat else None,expense_name=name,amount=data.amount,description=data.description,expense_date=data.expense_date,payment_status=data.payment_status,supplier=data.supplier,reference=data.reference,source_module=data.source_module or 'MANUAL')
    db.add(row);db.commit();db.refresh(row);return _serialize(row)

@router.get('/')
def list_all(project_id:int|None=None,db:Session=Depends(get_db),_=Depends(READ)):
    q=db.query(Expense)
    if project_id is not None:q=q.filter(Expense.project_id==project_id)
    return [_serialize(x) for x in q.order_by(Expense.id).all()]

@router.get('/{expense_id}')
def get_by_id(expense_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    x=db.query(Expense).filter(Expense.id==expense_id).first()
    if not x: raise HTTPException(404,'Expense not found')
    return _serialize(x)

@router.put('/{expense_id}')
def update(expense_id:int,data:ExpenseUpdate,db:Session=Depends(get_db),_=Depends(EDIT)):
    x=db.query(Expense).filter(Expense.id==expense_id).first()
    if not x:raise HTTPException(404,'Expense not found')
    p=data.model_dump(exclude_unset=True)
    if 'category' in p or 'category_id' in p:
        c=_category(db,p.pop('category',None),p.pop('category_id',None));x.category_id=c.id if c else None
    for k,v in p.items():setattr(x,k,v)
    db.commit();db.refresh(x);return _serialize(x)

@router.delete('/{expense_id}')
def delete(expense_id:int,db:Session=Depends(get_db),_=Depends(EDIT)):
    x=db.query(Expense).filter(Expense.id==expense_id).first()
    if not x:raise HTTPException(404,'Expense not found')
    db.delete(x);db.commit();return {'message':'Expense deleted successfully'}
