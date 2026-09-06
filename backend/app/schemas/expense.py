from datetime import date
from typing import Optional

from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    project_id: int
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    expense_name: str
    amount: float
    description: Optional[str] = None
    expense_date: Optional[date] = None
    payment_status: str = "Pending"
    supplier: Optional[str] = None


class ExpenseUpdate(BaseModel):
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    expense_name: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    expense_date: Optional[date] = None
    payment_status: Optional[str] = None
    supplier: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    project_id: int
    budget_id: Optional[int] = None
    category_id: Optional[int] = None
    expense_name: str
    amount: float
    description: Optional[str] = None
    expense_date: Optional[date] = None
    payment_status: str
    supplier: Optional[str] = None

    class Config:
        from_attributes = True