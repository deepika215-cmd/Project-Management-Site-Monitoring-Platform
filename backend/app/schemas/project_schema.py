from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Project Create Schema
# ---------------------------------------------------------

class ProjectCreate(BaseModel):

    project_name: str = Field(
        min_length=1,
        max_length=200
    )

    project_code: str = Field(
        min_length=1,
        max_length=50
    )

    project_category: Literal[
        "Residential",
        "Commercial",
        "Industrial",
        "Infrastructure",
        "Government"
    ]

    description: str

    location: str

    start_date: date

    end_date: date

    budget: int = Field(
        ge=0
    )

    priority: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    status: Literal[
        "Planning",
        "In Progress",
        "On Hold",
        "Completed",
        "Closed"
    ] = "Planning"

    manager_id: int


# ---------------------------------------------------------
# Project Response Schema
# ---------------------------------------------------------

class ProjectResponse(BaseModel):

    id: int

    project_name: str

    project_code: str | None = None

    project_category: str | None = None

    description: str

    location: str

    start_date: date

    end_date: date

    budget: int

    priority: str | None = None

    status: str

    manager_id: int

    # Project closure validation status
    inspection_approved: bool = False

    financial_settlement_complete: bool = False

    pending_issues_resolved: bool = False

    client_accepted: bool = False

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Project Status Update Schema
# ---------------------------------------------------------

class ProjectStatusUpdate(BaseModel):

    status: Literal[
        "Planning",
        "In Progress",
        "On Hold",
        "Completed",
        "Closed"
    ]


# ---------------------------------------------------------
# Project Closure Validation Update Schema
# ---------------------------------------------------------

class ProjectClosureUpdate(BaseModel):

    inspection_approved: bool

    financial_settlement_complete: bool

    pending_issues_resolved: bool

    client_accepted: bool
