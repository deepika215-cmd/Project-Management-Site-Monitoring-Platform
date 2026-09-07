from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.budget_category import BudgetCategory
from app.schemas.budget_category import BudgetCategoryCreate, BudgetCategoryResponse, BudgetCategoryUpdate
from app.core.permissions import role_required

router = APIRouter(prefix="/budget-categories", tags=["Budget Categories"])
READ = role_required(["ADMIN","PROJECT_MANAGER","SITE_ENGINEER","CLIENT"])
EDIT = role_required(["ADMIN","PROJECT_MANAGER"])

@router.post("/", response_model=BudgetCategoryResponse)
def create_budget_category(data: BudgetCategoryCreate, db: Session = Depends(get_db), _=Depends(EDIT)):
    existing=db.query(BudgetCategory).filter(BudgetCategory.name==data.name).first()
    if existing: raise HTTPException(400,"Budget category already exists")
    row=BudgetCategory(name=data.name, description=data.description); db.add(row); db.commit(); db.refresh(row); return row

@router.get("/", response_model=List[BudgetCategoryResponse])
def get_budget_categories(db: Session = Depends(get_db), _=Depends(READ)):
    return db.query(BudgetCategory).order_by(BudgetCategory.id).all()

@router.get("/{category_id}", response_model=BudgetCategoryResponse)
def get_budget_category(category_id:int,db:Session=Depends(get_db),_=Depends(READ)):
    row=db.query(BudgetCategory).filter(BudgetCategory.id==category_id).first()
    if not row: raise HTTPException(404,"Budget category not found")
    return row

@router.put("/{category_id}", response_model=BudgetCategoryResponse)
def update_budget_category(category_id:int,data:BudgetCategoryUpdate,db:Session=Depends(get_db),_=Depends(EDIT)):
    row=db.query(BudgetCategory).filter(BudgetCategory.id==category_id).first()
    if not row: raise HTTPException(404,"Budget category not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(row,k,v)
    db.commit(); db.refresh(row); return row

@router.delete("/{category_id}")
def delete_budget_category(category_id:int,db:Session=Depends(get_db),_=Depends(EDIT)):
    row=db.query(BudgetCategory).filter(BudgetCategory.id==category_id).first()
    if not row: raise HTTPException(404,"Budget category not found")
    if row.budgets or row.cost_estimates or row.expenses: raise HTTPException(400,"Category is in use and cannot be deleted")
    db.delete(row); db.commit(); return {"message":"Budget category deleted successfully"}
