from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.project import Project
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.schemas.cost_estimate import CostEstimateCreate, CostEstimateUpdate
from app.core.permissions import role_required

router=APIRouter(prefix='/cost-estimates',tags=['Cost Estimates'])
READ=role_required(['ADMIN','PROJECT_MANAGER','SITE_ENGINEER','CLIENT'])
EDIT=role_required(['ADMIN','PROJECT_MANAGER'])

def _key(v): return str(v or '').strip().upper().replace(' COST','').replace(' ','_')
def _category(db,name=None,cid=None):
    if cid:
        row=db.query(BudgetCategory).filter(BudgetCategory.id==cid).first()
        if not row: raise HTTPException(404,'Budget category not found')
        return row
    key=_key(name)
    if not key: return None
    labels={'LABOR':'Labor Cost','MATERIAL':'Material Cost','EQUIPMENT':'Equipment Cost','TRANSPORTATION':'Transportation Cost','MAINTENANCE':'Maintenance Cost','ADMINISTRATIVE':'Administrative Cost'}
    label=labels.get(key,str(name).replace('_',' ').title())
    row=db.query(BudgetCategory).filter(func.upper(BudgetCategory.name)==label.upper()).first()
    if not row: row=BudgetCategory(name=label); db.add(row); db.flush()
    return row

def _serialize(x):
    cat=x.category.name if x.category else None
    return {'id':x.id,'project_id':x.project_id,'budget_id':x.budget_id,'category_id':x.category_id,'category':_key(cat),'category_name':cat,'item_name':x.item_name,'activity':x.item_name,'quantity':x.quantity,'unit':x.unit,'unit_cost':x.unit_cost,'estimated_amount':x.estimated_amount,'description':x.description,'notes':x.description,'estimate_date':x.estimate_date}

@router.post('/')
def create(data:CostEstimateCreate,db:Session=Depends(get_db),_=Depends(EDIT)):
    if not db.query(Project).filter(Project.id==data.project_id).first(): raise HTTPException(404,'Project not found')
    if data.budget_id:
        b=db.query(Budget).filter(Budget.id==data.budget_id).first()
        if not b or b.project_id!=data.project_id: raise HTTPException(400,'Budget does not belong to this project')
    cat=_category(db,data.category,data.category_id)
    item=(data.item_name or data.activity or '').strip()
    if not item: raise HTTPException(422,'Activity/item name is required')
    amount=data.estimated_amount if data.estimated_amount is not None else data.quantity*data.unit_cost
    row=CostEstimate(project_id=data.project_id,budget_id=data.budget_id,category_id=cat.id if cat else None,item_name=item,quantity=data.quantity,unit=data.unit,unit_cost=data.unit_cost,estimated_amount=amount,description=data.description or data.notes,estimate_date=data.estimate_date)
    db.add(row); db.commit(); db.refresh(row); return _serialize(row)

@router.get('/')
def list_all(project_id:int|None=None,db:Session=Depends(get_db),_=Depends(READ)):
    q=db.query(CostEstimate)
    if project_id is not None:q=q.filter(CostEstimate.project_id==project_id)
    return [_serialize(x) for x in q.order_by(CostEstimate.id).all()]

@router.get('/{estimate_id}')
def get_by_id(estimate_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    x=db.query(CostEstimate).filter(CostEstimate.id==estimate_id).first()
    if not x: raise HTTPException(404,'Cost estimate not found')
    return _serialize(x)

@router.put('/{estimate_id}')
def update(estimate_id:int,data:CostEstimateUpdate,db:Session=Depends(get_db),_=Depends(EDIT)):
    x=db.query(CostEstimate).filter(CostEstimate.id==estimate_id).first()
    if not x: raise HTTPException(404,'Cost estimate not found')
    p=data.model_dump(exclude_unset=True)
    if 'category' in p or 'category_id' in p:
        c=_category(db,p.pop('category',None),p.pop('category_id',None)); x.category_id=c.id if c else None
    if 'activity' in p and 'item_name' not in p:p['item_name']=p.pop('activity')
    if 'notes' in p and 'description' not in p:p['description']=p.pop('notes')
    for k,v in p.items(): setattr(x,k,v)
    if ('quantity' in p or 'unit_cost' in p) and 'estimated_amount' not in p:x.estimated_amount=x.quantity*x.unit_cost
    db.commit(); db.refresh(x); return _serialize(x)

@router.delete('/{estimate_id}')
def delete(estimate_id:int,db:Session=Depends(get_db),_=Depends(EDIT)):
    x=db.query(CostEstimate).filter(CostEstimate.id==estimate_id).first()
    if not x: raise HTTPException(404,'Cost estimate not found')
    db.delete(x); db.commit(); return {'message':'Cost estimate deleted successfully'}
