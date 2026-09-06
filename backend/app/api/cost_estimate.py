from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.cost_estimate import CostEstimate
from app.models.project import Project
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.schemas.cost_estimate import (
    CostEstimateCreate,
    CostEstimateResponse,
    CostEstimateUpdate,
)


router = APIRouter(
    prefix="/cost-estimates",
    tags=["Cost Estimates"],
)


@router.post(
    "/",
    response_model=CostEstimateResponse,
)
def create_cost_estimate(
    data: CostEstimateCreate,
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

    estimated_amount = data.estimated_amount

    if estimated_amount is None:
        estimated_amount = (
            data.quantity * data.unit_cost
        )

    estimate = CostEstimate(
        project_id=data.project_id,
        budget_id=data.budget_id,
        category_id=data.category_id,
        item_name=data.item_name,
        quantity=data.quantity,
        unit=data.unit,
        unit_cost=data.unit_cost,
        estimated_amount=estimated_amount,
        description=data.description,
        estimate_date=data.estimate_date,
    )

    db.add(estimate)
    db.commit()
    db.refresh(estimate)

    return estimate


@router.get(
    "/",
    response_model=List[CostEstimateResponse],
)
def get_cost_estimates(
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(CostEstimate)

    if project_id is not None:
        query = query.filter(
            CostEstimate.project_id == project_id
        )

    return query.order_by(CostEstimate.id).all()


@router.get(
    "/{estimate_id}",
    response_model=CostEstimateResponse,
)
def get_cost_estimate(
    estimate_id: int,
    db: Session = Depends(get_db),
):
    estimate = (
        db.query(CostEstimate)
        .filter(CostEstimate.id == estimate_id)
        .first()
    )

    if not estimate:
        raise HTTPException(
            status_code=404,
            detail="Cost estimate not found",
        )

    return estimate


@router.put(
    "/{estimate_id}",
    response_model=CostEstimateResponse,
)
def update_cost_estimate(
    estimate_id: int,
    data: CostEstimateUpdate,
    db: Session = Depends(get_db),
):
    estimate = (
        db.query(CostEstimate)
        .filter(CostEstimate.id == estimate_id)
        .first()
    )

    if not estimate:
        raise HTTPException(
            status_code=404,
            detail="Cost estimate not found",
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(estimate, key, value)

    if (
        "quantity" in updates
        or "unit_cost" in updates
    ) and "estimated_amount" not in updates:
        estimate.estimated_amount = (
            estimate.quantity * estimate.unit_cost
        )

    db.commit()
    db.refresh(estimate)

    return estimate


@router.delete("/{estimate_id}")
def delete_cost_estimate(
    estimate_id: int,
    db: Session = Depends(get_db),
):
    estimate = (
        db.query(CostEstimate)
        .filter(CostEstimate.id == estimate_id)
        .first()
    )

    if not estimate:
        raise HTTPException(
            status_code=404,
            detail="Cost estimate not found",
        )

    db.delete(estimate)
    db.commit()

    return {
        "message": "Cost estimate deleted successfully"
    }