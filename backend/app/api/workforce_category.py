from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.workforce_category import WorkforceCategory
from app.schemas.workforce_category_schema import (
    WorkforceCategoryCreate,
    WorkforceCategoryResponse
)


router = APIRouter(
    prefix="/workforce-categories",
    tags=["Workforce Categories"]
)


# ============================================================
# CREATE WORKFORCE CATEGORY
# ============================================================

@router.post(
    "/",
    response_model=WorkforceCategoryResponse
)
def create_workforce_category(
    category: WorkforceCategoryCreate,
    db: Session = Depends(get_db)
):

    existing_category = (
        db.query(WorkforceCategory)
        .filter(
            WorkforceCategory.name == category.name
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Workforce category already exists"
        )

    new_category = WorkforceCategory(
        **category.model_dump()
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# ============================================================
# GET ALL WORKFORCE CATEGORIES
# ============================================================

@router.get(
    "/",
    response_model=list[WorkforceCategoryResponse]
)
def get_workforce_categories(
    db: Session = Depends(get_db)
):

    return (
        db.query(WorkforceCategory)
        .order_by(WorkforceCategory.id)
        .all()
    )


# ============================================================
# GET WORKFORCE CATEGORY BY ID
# ============================================================

@router.get(
    "/{category_id}",
    response_model=WorkforceCategoryResponse
)
def get_workforce_category(
    category_id: int,
    db: Session = Depends(get_db)
):

    category = (
        db.query(WorkforceCategory)
        .filter(
            WorkforceCategory.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Workforce category not found"
        )

    return category


# ============================================================
# UPDATE WORKFORCE CATEGORY
# ============================================================

@router.put(
    "/{category_id}",
    response_model=WorkforceCategoryResponse
)
def update_workforce_category(
    category_id: int,
    category_data: WorkforceCategoryCreate,
    db: Session = Depends(get_db)
):

    category = (
        db.query(WorkforceCategory)
        .filter(
            WorkforceCategory.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Workforce category not found"
        )

    duplicate = (
        db.query(WorkforceCategory)
        .filter(
            WorkforceCategory.name == category_data.name,
            WorkforceCategory.id != category_id
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another workforce category with this name already exists"
        )

    for key, value in category_data.model_dump().items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


# ============================================================
# DELETE WORKFORCE CATEGORY
# ============================================================

@router.delete("/{category_id}")
def delete_workforce_category(
    category_id: int,
    db: Session = Depends(get_db)
):

    category = (
        db.query(WorkforceCategory)
        .filter(
            WorkforceCategory.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Workforce category not found"
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Workforce category deleted successfully"
    }