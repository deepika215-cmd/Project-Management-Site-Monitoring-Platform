from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.project import Project
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.models.expense import Expense
from app.schemas.budget import BudgetPlanCreate, BudgetPlanUpdate
from app.core.permissions import role_required

router=APIRouter(prefix="/budgets",tags=["Budgets"])
READ=role_required(["ADMIN","PROJECT_MANAGER","SITE_ENGINEER","CLIENT"])
EDIT=role_required(["ADMIN","PROJECT_MANAGER"])
CANONICAL=[("LABOR","Labor Cost"),("MATERIAL","Material Cost"),("EQUIPMENT","Equipment Cost"),("TRANSPORTATION","Transportation Cost"),("MAINTENANCE","Maintenance Cost"),("ADMINISTRATIVE","Administrative Cost")]

def _key(v): return str(v or '').strip().upper().replace(' COST','').replace(' ','_')
def _category(db,name):
    key=_key(name)
    label=next((label for k,label in CANONICAL if k==key), str(name or key).replace('_',' ').title())
    row=db.query(BudgetCategory).filter(func.upper(BudgetCategory.name)==label.upper()).first()
    if not row:
        row=BudgetCategory(name=label); db.add(row); db.flush()
    return row

def _project(db,pid):
    p=db.query(Project).filter(Project.id==pid).first()
    if not p: raise HTTPException(404,"Project not found")
    return p

def _serialize_plan(db,pid):
    rows=db.query(Budget).filter(Budget.project_id==pid).order_by(Budget.id).all()
    if not rows: return None
    alloc=[]
    for r in rows:
        name=r.category.name if r.category else "Uncategorized"
        alloc.append({"category":_key(name),"category_name":name,"category_id":r.category_id,"amount":float(r.allocated_amount or 0),"allocated_amount":float(r.allocated_amount or 0)})
    return {"id":rows[0].id,"project_id":pid,"total_budget":round(sum(x["amount"] for x in alloc),2),"category_allocations":alloc,"allocations":alloc,"status":rows[0].status or "Active","description":rows[0].description,"start_date":rows[0].start_date,"end_date":rows[0].end_date}

def _save_plan(db,pid,data):
    _project(db,pid)
    payload=data.model_dump(exclude_unset=True)
    allocations=payload.get('category_allocations') or []
    if not allocations and payload.get('allocated_amount') is not None:
        allocations=[{"category":"ADMINISTRATIVE","amount":payload['allocated_amount']}]
    if not allocations and payload.get('total_budget') is not None:
        allocations=[{"category":"ADMINISTRATIVE","amount":payload['total_budget']}]
    if not allocations:
        raise HTTPException(422,"At least one category allocation is required")

    cleaned=[]
    for item in allocations:
        item=item if isinstance(item,dict) else item.model_dump()
        category=item.get('category') or item.get('category_name') or item.get('name')
        amount=float(item.get('amount') if item.get('amount') is not None else item.get('allocated_amount') or 0)
        if amount < 0:
            raise HTTPException(422,"Budget allocation amount cannot be negative")
        cleaned.append({"category":category,"amount":amount})

    if sum(x["amount"] for x in cleaned) <= 0:
        raise HTTPException(422,"Total budget must be greater than zero")

    db.query(Budget).filter(Budget.project_id==pid).delete(synchronize_session=False)
    db.flush()
    for item in cleaned:
        cat=_category(db,item.get('category'))
        db.add(Budget(
            project_id=pid,
            category_id=cat.id,
            allocated_amount=item["amount"],
            description=payload.get('description'),
            status=payload.get('status') or 'Active',
            start_date=payload.get('start_date'),
            end_date=payload.get('end_date')
        ))
    db.commit()
    return _serialize_plan(db,pid)

@router.get("/project/{project_id}")
def get_budget_plan(project_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    _project(db,project_id); return _serialize_plan(db,project_id)

@router.get("/project/{project_id}/summary")
def get_budget_summary(project_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    _project(db,project_id)
    total=float(db.query(func.coalesce(func.sum(Budget.allocated_amount),0)).filter(Budget.project_id==project_id).scalar() or 0)
    estimated=float(db.query(func.coalesce(func.sum(CostEstimate.estimated_amount),0)).filter(CostEstimate.project_id==project_id).scalar() or 0)
    spent=float(db.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.project_id==project_id).scalar() or 0)
    util=round(spent/total*100,2) if total else 0
    status='Over Budget' if spent>total and total else ('Critical' if util>=90 else 'Warning' if util>=75 else 'Within Budget')
    return {"project_id":project_id,"total_budget":round(total,2),"estimated_cost":round(estimated,2),"total_estimated":round(estimated,2),"amount_spent":round(spent,2),"actual_cost":round(spent,2),"total_actual":round(spent,2),"remaining_budget":round(total-spent,2),"utilization_percentage":util,"status":status}

@router.post("/")
def create_budget(data:BudgetPlanCreate,db:Session=Depends(get_db),_=Depends(EDIT)):
    # Upsert behavior keeps the Angular page simple and prevents a stale/null
    # budgetPlan from turning a second save into a 409 conflict.
    return _save_plan(db,data.project_id,data)

@router.get("/")
def get_budgets(project_id:int|None=None,db:Session=Depends(get_db),_=Depends(READ)):
    if project_id is not None: return [_serialize_plan(db,project_id)] if _serialize_plan(db,project_id) else []
    ids=[x[0] for x in db.query(Budget.project_id).distinct().all()]; return [_serialize_plan(db,pid) for pid in ids]

@router.get("/{budget_id}")
def get_budget_by_id(budget_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    """Return the complete budget plan that contains the requested budget row."""
    row=db.query(Budget).filter(Budget.id==budget_id).first()
    if not row: raise HTTPException(404,"Budget plan not found")
    return _serialize_plan(db,row.project_id)

@router.put("/{budget_id}")
def update_budget(budget_id:int,data:BudgetPlanUpdate,db:Session=Depends(get_db),_=Depends(EDIT)):
    row=db.query(Budget).filter(Budget.id==budget_id).first()
    if not row: raise HTTPException(404,"Budget plan not found")
    return _save_plan(db,row.project_id,data)

@router.delete("/{budget_id}")
def delete_budget(budget_id:int,db:Session=Depends(get_db),_=Depends(EDIT)):
    row=db.query(Budget).filter(Budget.id==budget_id).first()
    if not row: raise HTTPException(404,"Budget plan not found")
    pid=row.project_id; db.query(Budget).filter(Budget.project_id==pid).delete(synchronize_session=False); db.commit(); return {"message":"Budget plan deleted successfully"}
