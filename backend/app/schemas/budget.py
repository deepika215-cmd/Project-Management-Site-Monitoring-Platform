from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BudgetBase(BaseModel):
    project_id: int
    category_id: Optional[int] = None

    allocated_amount: float = Field(
        ...,
        ge=0,
    )

    description: Optional[str] = None

    status: str = "Active"

    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    allocated_amount: Optional[float] = Field(
        default=None,
        ge=0,
    )
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetResponse(BudgetBase):
    id: int

    model_config = ConfigDict(from_attributes=True)