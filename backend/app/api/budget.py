from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.project import Project
from app.schemas.budget import (
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
)


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)


@router.post(
    "/",
    response_model=BudgetResponse,
)
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == data.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if data.category_id is not None:
        category = (
            db.query(BudgetCategory)
            .filter(
                BudgetCategory.id == data.category_id
            )
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Budget category not found",
            )

    budget = Budget(
        project_id=data.project_id,
        category_id=data.category_id,
        allocated_amount=data.allocated_amount,
        description=data.description,
        status=data.status,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return budget


@router.get(
    "/",
    response_model=List[BudgetResponse],
)
def get_budgets(
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Budget)

    if project_id is not None:
        query = query.filter(
            Budget.project_id == project_id
        )

    return query.order_by(Budget.id).all()


@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    return budget


@router.put(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    if data.category_id is not None:
        category = (
            db.query(BudgetCategory)
            .filter(
                BudgetCategory.id == data.category_id
            )
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Budget category not found",
            )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(budget, key, value)

    db.commit()
    db.refresh(budget)

    return budget


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found",
        )

    db.delete(budget)
    db.commit()

    return {
        "message": "Budget deleted successfully"
    }