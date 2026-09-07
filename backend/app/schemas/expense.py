from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
class ExpenseCreate(BaseModel):
    project_id: int
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    expense_name: Optional[str] = None
    amount: float = Field(ge=0)
    description: Optional[str] = None
    expense_date: Optional[date] = None
    payment_status: str = "Pending"
    supplier: Optional[str] = None
    reference: Optional[str] = None
    source_module: Optional[str] = "MANUAL"
class ExpenseUpdate(BaseModel):
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    category: Optional[str] = None
    expense_name: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    expense_date: Optional[date] = None
    payment_status: Optional[str] = None
    supplier: Optional[str] = None
    reference: Optional[str] = None
    source_module: Optional[str] = None
