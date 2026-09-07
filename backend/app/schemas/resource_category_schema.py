from typing import Optional

from pydantic import BaseModel


class ResourceCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "Active"


class ResourceCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str

    class Config:
        from_attributes = True