from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.budget import Budget
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.models.expense import Expense
from app.models.project import Project


router = APIRouter(
    prefix="/budget-monitoring",
    tags=["Budget Monitoring"],
)


def calculate_percentage(
    value: float,
    total: float,
) -> float:
    if total == 0:
        return 0.0

    return round(
        (value / total) * 100,
        2,
    )


@router.get(
    "/project/{project_id}"
)
def get_budget_monitoring(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    total_budget = (
        db.query(
            func.coalesce(
                func.sum(Budget.allocated_amount),
                0,
            )
        )
        .filter(
            Budget.project_id == project_id
        )
        .scalar()
        or 0
    )

    total_estimated = (
        db.query(
            func.coalesce(
                func.sum(
                    CostEstimate.estimated_amount
                ),
                0,
            )
        )
        .filter(
            CostEstimate.project_id == project_id
        )
        .scalar()
        or 0
    )

    total_actual = (
        db.query(
            func.coalesce(
                func.sum(Expense.amount),
                0,
            )
        )
        .filter(
            Expense.project_id == project_id
        )
        .scalar()
        or 0
    )

    remaining_budget = (
        total_budget - total_actual
    )

    utilization = calculate_percentage(
        total_actual,
        total_budget,
    )

    if total_actual > total_budget:
        status = "Over Budget"
    elif utilization >= 90:
        status = "Critical"
    elif utilization >= 75:
        status = "Warning"
    else:
        status = "Within Budget"

    categories = []

    category_ids = set()

    budget_category_ids = (
        db.query(Budget.category_id)
        .filter(
            Budget.project_id == project_id,
            Budget.category_id.isnot(None),
        )
        .distinct()
        .all()
    )

    estimate_category_ids = (
        db.query(CostEstimate.category_id)
        .filter(
            CostEstimate.project_id == project_id,
            CostEstimate.category_id.isnot(None),
        )
        .distinct()
        .all()
    )

    expense_category_ids = (
        db.query(Expense.category_id)
        .filter(
            Expense.project_id == project_id,
            Expense.category_id.isnot(None),
        )
        .distinct()
        .all()
    )

    for item in (
        budget_category_ids
        + estimate_category_ids
        + expense_category_ids
    ):
        if item[0] is not None:
            category_ids.add(item[0])

    for category_id in sorted(category_ids):
        category = (
            db.query(BudgetCategory)
            .filter(
                BudgetCategory.id == category_id
            )
            .first()
        )

        category_name = (
            category.name
            if category
            else "Unknown"
        )

        allocated = (
            db.query(
                func.coalesce(
                    func.sum(
                        Budget.allocated_amount
                    ),
                    0,
                )
            )
            .filter(
                Budget.project_id == project_id,
                Budget.category_id == category_id,
            )
            .scalar()
            or 0
        )

        estimated = (
            db.query(
                func.coalesce(
                    func.sum(
                        CostEstimate.estimated_amount
                    ),
                    0,
                )
            )
            .filter(
                CostEstimate.project_id
                == project_id,
                CostEstimate.category_id
                == category_id,
            )
            .scalar()
            or 0
        )

        actual = (
            db.query(
                func.coalesce(
                    func.sum(Expense.amount),
                    0,
                )
            )
            .filter(
                Expense.project_id == project_id,
                Expense.category_id
                == category_id,
            )
            .scalar()
            or 0
        )

        remaining = allocated - actual

        category_utilization = (
            calculate_percentage(
                actual,
                allocated,
            )
        )

        categories.append(
            {
                "category_id": category_id,
                "category_name": category_name,
                "allocated": round(
                    float(allocated),
                    2,
                ),
                "estimated": round(
                    float(estimated),
                    2,
                ),
                "actual": round(
                    float(actual),
                    2,
                ),
                "remaining": round(
                    float(remaining),
                    2,
                ),
                "utilization_percentage":
                    category_utilization,
                "difference": round(
                    float(actual - estimated),
                    2,
                ),
            }
        )

    return {
        "project_id": project_id,
        "total_budget": round(
            float(total_budget),
            2,
        ),
        "total_estimated": round(
            float(total_estimated),
            2,
        ),
        "total_actual": round(
            float(total_actual),
            2,
        ),
        "remaining_budget": round(
            float(remaining_budget),
            2,
        ),
        "utilization_percentage": utilization,
        "status": status,
        "categories": categories,
    }
    