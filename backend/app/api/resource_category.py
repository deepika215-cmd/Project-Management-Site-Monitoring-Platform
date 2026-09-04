from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.permissions import role_required

from app.models.resource_category import ResourceCategory
from app.models.user import User

from app.schemas.resource_category_schema import (
    ResourceCategoryCreate,
    ResourceCategoryResponse
)


router = APIRouter(
    prefix="/resource-categories",
    tags=["Resource Categories"]
)


# =========================================================
# CREATE RESOURCE CATEGORY
# Allowed roles: ADMIN, MANAGER
# =========================================================

@router.post(
    "/",
    response_model=ResourceCategoryResponse
)
def create_resource_category(
    category: ResourceCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    )
):
    existing_category = db.query(
        ResourceCategory
    ).filter(
        ResourceCategory.name == category.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Resource category already exists"
        )

    new_category = ResourceCategory(
        name=category.name,
        description=category.description,
        status=category.status
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# =========================================================
# GET ALL RESOURCE CATEGORIES
# Allowed roles: ADMIN, MANAGER, ENGINEER
# =========================================================

@router.get(
    "/",
    response_model=list[ResourceCategoryResponse]
)
def get_resource_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):
    return db.query(ResourceCategory).all()


# =========================================================
# GET RESOURCE CATEGORY BY ID
# Allowed roles: ADMIN, MANAGER, ENGINEER
# =========================================================

@router.get(
    "/{category_id}",
    response_model=ResourceCategoryResponse
)
def get_resource_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    )
):
    category = db.query(
        ResourceCategory
    ).filter(
        ResourceCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Resource category not found"
        )

    return category