from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
class CategoryAllocation(BaseModel):
    category: str
    amount: float = Field(ge=0)
class BudgetPlanCreate(BaseModel):
    project_id: int
    total_budget: Optional[float] = Field(default=None, ge=0)
    category_allocations: List[CategoryAllocation] = []
    category_id: Optional[int] = None
    allocated_amount: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    status: str = "Active"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
class BudgetPlanUpdate(BudgetPlanCreate):
    project_id: Optional[int] = None
