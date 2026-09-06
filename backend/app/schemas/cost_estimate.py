from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CostEstimateBase(BaseModel):
    project_id: int
    budget_id: Optional[int] = None
    category_id: Optional[int] = None

    item_name: str

    quantity: float = Field(
        default=1.0,
        gt=0,
    )

    unit: Optional[str] = None

    unit_cost: float = Field(
        default=0.0,
        ge=0,
    )

    estimated_amount: Optional[float] = Field(
        default=None,
        ge=0,
    )

    description: Optional[str] = None
    estimate_date: Optional[date] = None


class CostEstimateCreate(CostEstimateBase):
    pass


class CostEstimateUpdate(BaseModel):
    budget_id: Optional[int] = None
    category_id: Optional[int] = None

    item_name: Optional[str] = None

    quantity: Optional[float] = Field(
        default=None,
        gt=0,
    )

    unit: Optional[str] = None

    unit_cost: Optional[float] = Field(
        default=None,
        ge=0,
    )

    estimated_amount: Optional[float] = Field(
        default=None,
        ge=0,
    )

    description: Optional[str] = None
    estimate_date: Optional[date] = None


class CostEstimateResponse(CostEstimateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)