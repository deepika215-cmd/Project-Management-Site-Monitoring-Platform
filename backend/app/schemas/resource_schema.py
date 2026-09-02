from pydantic import BaseModel, Field


# =========================================================
# Resource Create Schema
# =========================================================

class ResourceCreate(BaseModel):
    name: str
    type: str
    quantity: int = Field(ge=0)
    status: str = "Available"
    project_id: int


# =========================================================
# Resource Response Schema
# =========================================================

class ResourceResponse(BaseModel):
    id: int
    name: str
    type: str
    quantity: int
    allocated_quantity: int
    status: str
    project_id: int

    class Config:
        from_attributes = True


# =========================================================
# Resource Allocation Schema
# =========================================================

class ResourceAllocation(BaseModel):
    quantity: int = Field(gt=0)


# =========================================================
# Resource Utilization Schema
# =========================================================

class ResourceUtilization(BaseModel):
    resource_id: int
    resource_name: str
    total_quantity: int
    allocated_quantity: int
    available_quantity: int
    utilization_percentage: float
    status: str


# =========================================================
# Resource Availability Schema
# =========================================================

class ResourceAvailability(BaseModel):
    resource_id: int
    resource_name: str
    type: str
    project_id: int
    total_quantity: int
    allocated_quantity: int
    available_quantity: int
    status: str