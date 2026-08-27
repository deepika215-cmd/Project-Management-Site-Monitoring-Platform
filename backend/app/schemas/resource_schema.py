from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    name: str
    type: str
    quantity: int = Field(ge=0)
    status: str = "Available"
    project_id: int


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


class ResourceAllocation(BaseModel):
    quantity: int = Field(gt=0)


class ResourceUtilization(BaseModel):
    resource_id: int
    resource_name: str
    total_quantity: int
    allocated_quantity: int
    available_quantity: int
    utilization_percentage: float
    status: str