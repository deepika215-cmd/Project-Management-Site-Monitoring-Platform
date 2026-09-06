from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.budget_category import BudgetCategory
from app.models.cost_estimate import CostEstimate
from app.models.expense import Expense
from app.models.project import Project
from app.schemas.cost_comparison import (
    CostComparisonItem,
    CostComparisonResponse,
)


router = APIRouter(
    prefix="/cost-comparison",
    tags=["Cost Comparison"],
)


def percentage(
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
    "/project/{project_id}",
    response_model=CostComparisonResponse,
)
def get_cost_comparison(
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
            CostEstimate.project_id
            == project_id
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
            Expense.project_id
            == project_id
        )
        .scalar()
        or 0
    )

    difference = (
        total_actual - total_estimated
    )

    variance_percentage = percentage(
        difference,
        total_estimated,
    )

    if total_actual > total_estimated:
        overall_status = "Over Estimate"
    elif total_actual < total_estimated:
        overall_status = "Under Estimate"
    else:
        overall_status = "On Estimate"

    category_ids = set()

    estimate_categories = (
        db.query(CostEstimate.category_id)
        .filter(
            CostEstimate.project_id
            == project_id,
            CostEstimate.category_id.isnot(None),
        )
        .distinct()
        .all()
    )

    expense_categories = (
        db.query(Expense.category_id)
        .filter(
            Expense.project_id
            == project_id,
            Expense.category_id.isnot(None),
        )
        .distinct()
        .all()
    )

    for item in (
        estimate_categories
        + expense_categories
    ):
        if item[0] is not None:
            category_ids.add(item[0])

    categories = []

    for category_id in sorted(category_ids):
        category = (
            db.query(BudgetCategory)
            .filter(
                BudgetCategory.id
                == category_id
            )
            .first()
        )

        category_name = (
            category.name
            if category
            else "Unknown"
        )

        estimated = (
            db.query(
                func.coalesce(
                    func.sum(
                        CostEstimate
                        .estimated_amount
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
                Expense.project_id
                == project_id,
                Expense.category_id
                == category_id,
            )
            .scalar()
            or 0
        )

        category_difference = (
            actual - estimated
        )

        category_variance = percentage(
            category_difference,
            estimated,
        )

        if actual > estimated:
            category_status = "Over Estimate"
        elif actual < estimated:
            category_status = "Under Estimate"
        else:
            category_status = "On Estimate"

        categories.append(
            CostComparisonItem(
                category_id=category_id,
                category_name=category_name,
                estimated=round(
                    float(estimated),
                    2,
                ),
                actual=round(
                    float(actual),
                    2,
                ),
                difference=round(
                    float(category_difference),
                    2,
                ),
                variance_percentage=
                    category_variance,
                status=category_status,
            )
        )

    return CostComparisonResponse(
        project_id=project_id,
        total_estimated=round(
            float(total_estimated),
            2,
        ),
        total_actual=round(
            float(total_actual),
            2,
        ),
        difference=round(
            float(difference),
            2,
        ),
        variance_percentage=
            variance_percentage,
        status=overall_status,
        categories=categories,
    )