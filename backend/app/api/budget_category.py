from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.budget_category import BudgetCategory
from app.schemas.budget_category import (
    BudgetCategoryCreate,
    BudgetCategoryResponse,
    BudgetCategoryUpdate,
)


router = APIRouter(
    prefix="/budget-categories",
    tags=["Budget Categories"],
)


@router.post(
    "/",
    response_model=BudgetCategoryResponse,
)
def create_budget_category(
    data: BudgetCategoryCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(BudgetCategory)
        .filter(BudgetCategory.name == data.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget category already exists",
        )

    category = BudgetCategory(
        name=data.name,
        description=data.description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get(
    "/",
    response_model=List[BudgetCategoryResponse],
)
def get_budget_categories(
    db: Session = Depends(get_db),
):
    return (
        db.query(BudgetCategory)
        .order_by(BudgetCategory.id)
        .all()
    )


@router.get(
    "/{category_id}",
    response_model=BudgetCategoryResponse,
)
def get_budget_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = (
        db.query(BudgetCategory)
        .filter(BudgetCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Budget category not found",
        )

    return category


@router.put(
    "/{category_id}",
    response_model=BudgetCategoryResponse,
)
def update_budget_category(
    category_id: int,
    data: BudgetCategoryUpdate,
    db: Session = Depends(get_db),
):
    category = (
        db.query(BudgetCategory)
        .filter(BudgetCategory.id == category_id)
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

    if "name" in updates:
        duplicate = (
            db.query(BudgetCategory)
            .filter(
                BudgetCategory.name == updates["name"],
                BudgetCategory.id != category_id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Budget category already exists",
            )

    for key, value in updates.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_budget_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = (
        db.query(BudgetCategory)
        .filter(BudgetCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Budget category not found",
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Budget category deleted successfully"
    }