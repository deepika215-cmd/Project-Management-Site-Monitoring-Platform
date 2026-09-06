from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.expense import Expense
from app.models.project import Project
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
)


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=ExpenseResponse,
)
def create_expense(
    data: ExpenseCreate,
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

    if data.budget_id is not None:
        budget = (
            db.query(Budget)
            .filter(Budget.id == data.budget_id)
            .first()
        )

        if not budget:
            raise HTTPException(
                status_code=404,
                detail="Budget not found",
            )

        if budget.project_id != data.project_id:
            raise HTTPException(
                status_code=400,
                detail="Budget does not belong to this project",
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

    expense = Expense(
        project_id=data.project_id,
        budget_id=data.budget_id,
        category_id=data.category_id,
        expense_name=data.expense_name,
        amount=data.amount,
        description=data.description,
        expense_date=data.expense_date,
        payment_status=data.payment_status,
        supplier=data.supplier,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get(
    "/",
    response_model=List[ExpenseResponse],
)
def get_expenses(
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Expense)

    if project_id is not None:
        query = query.filter(
            Expense.project_id == project_id
        )

    return query.order_by(Expense.id).all()


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    return expense


@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)

    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully"
    }