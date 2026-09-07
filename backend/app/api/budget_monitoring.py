from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.project import Project
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.models.expense import Expense
from app.core.permissions import role_required
router=APIRouter(prefix='/budget-monitoring',tags=['Budget Monitoring'])
READ=role_required(['ADMIN','PROJECT_MANAGER','SITE_ENGINEER','CLIENT'])

def pct(v,t): return round(float(v)/float(t)*100,2) if t else 0.0
@router.get('/project/{project_id}')
def monitoring(project_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    if not db.query(Project).filter(Project.id==project_id).first():raise HTTPException(404,'Project not found')
    total=float(db.query(func.coalesce(func.sum(Budget.allocated_amount),0)).filter(Budget.project_id==project_id).scalar() or 0)
    est=float(db.query(func.coalesce(func.sum(CostEstimate.estimated_amount),0)).filter(CostEstimate.project_id==project_id).scalar() or 0)
    actual=float(db.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.project_id==project_id).scalar() or 0)
    util=pct(actual,total)
    status='Over Budget' if total and actual>total else ('Critical' if util>=90 else 'Warning' if util>=75 else 'Within Budget')
    cats=[]
    for c in db.query(BudgetCategory).order_by(BudgetCategory.id).all():
        allocated=float(db.query(func.coalesce(func.sum(Budget.allocated_amount),0)).filter(Budget.project_id==project_id,Budget.category_id==c.id).scalar() or 0)
        ce=float(db.query(func.coalesce(func.sum(CostEstimate.estimated_amount),0)).filter(CostEstimate.project_id==project_id,CostEstimate.category_id==c.id).scalar() or 0)
        ac=float(db.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.project_id==project_id,Expense.category_id==c.id).scalar() or 0)
        if allocated or ce or ac: cats.append({'category_id':c.id,'category_name':c.name,'allocated':round(allocated,2),'estimated':round(ce,2),'actual':round(ac,2),'remaining':round(allocated-ac,2),'utilization_percentage':pct(ac,allocated),'difference':round(ac-ce,2)})
    return {'project_id':project_id,'total_budget':round(total,2),'total_estimated':round(est,2),'total_actual':round(actual,2),'remaining_budget':round(total-actual,2),'utilization_percentage':util,'status':status,'categories':cats}
