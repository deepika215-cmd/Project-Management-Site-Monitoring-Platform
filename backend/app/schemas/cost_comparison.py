from typing import List

from pydantic import BaseModel


class CostComparisonItem(BaseModel):
    category_id: int | None = None
    category_name: str

    estimated: float
    actual: float

    difference: float
    variance_percentage: float

    status: str


class CostComparisonResponse(BaseModel):
    project_id: int

    total_estimated: float
    total_actual: float

    difference: float
    variance_percentage: float

    status: str

    categories: List[CostComparisonItem]    