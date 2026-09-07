from typing import Optional
from pydantic import BaseModel, ConfigDict
class BudgetCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
class BudgetCategoryCreate(BudgetCategoryBase): pass
class BudgetCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
class BudgetCategoryResponse(BudgetCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
