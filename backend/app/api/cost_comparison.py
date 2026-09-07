from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.project import Project
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.models.expense import Expense
from app.core.permissions import role_required
router=APIRouter(prefix='/cost-comparison',tags=['Cost Comparison'])
READ=role_required(['ADMIN','PROJECT_MANAGER','SITE_ENGINEER','CLIENT'])
def pct(v,t): return round(float(v)/float(t)*100,2) if t else 0.0
@router.get('/project/{project_id}')
def comparison(project_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    if not db.query(Project).filter(Project.id==project_id).first():raise HTTPException(404,'Project not found')
    est=float(db.query(func.coalesce(func.sum(CostEstimate.estimated_amount),0)).filter(CostEstimate.project_id==project_id).scalar() or 0)
    actual=float(db.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.project_id==project_id).scalar() or 0)
    diff=actual-est; status='Over Estimate' if diff>0 else 'Under Estimate' if diff<0 else 'On Estimate'; cats=[]
    for c in db.query(BudgetCategory).order_by(BudgetCategory.id).all():
        e=float(db.query(func.coalesce(func.sum(CostEstimate.estimated_amount),0)).filter(CostEstimate.project_id==project_id,CostEstimate.category_id==c.id).scalar() or 0)
        a=float(db.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.project_id==project_id,Expense.category_id==c.id).scalar() or 0)
        if e or a:
            d=a-e; cats.append({'category_id':c.id,'category_name':c.name,'estimated':round(e,2),'actual':round(a,2),'difference':round(d,2),'variance_percentage':pct(d,e),'status':'Over Estimate' if d>0 else 'Under Estimate' if d<0 else 'On Estimate'})
    return {'project_id':project_id,'total_estimated':round(est,2),'total_actual':round(actual,2),'difference':round(diff,2),'variance_percentage':pct(diff,est),'status':status,'categories':cats}
