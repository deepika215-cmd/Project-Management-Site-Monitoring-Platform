from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
class CostEstimateCreate(BaseModel):
    project_id: int
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    item_name: Optional[str] = None
    activity: Optional[str] = None
    quantity: float = Field(default=1.0, gt=0)
    unit: Optional[str] = None
    unit_cost: float = Field(default=0.0, ge=0)
    estimated_amount: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    notes: Optional[str] = None
    estimate_date: Optional[date] = None
class CostEstimateUpdate(BaseModel):
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    item_name: Optional[str] = None
    activity: Optional[str] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None
    unit_cost: Optional[float] = Field(default=None, ge=0)
    estimated_amount: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    notes: Optional[str] = None
    estimate_date: Optional[date] = None
