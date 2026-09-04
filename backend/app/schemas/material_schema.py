from pydantic import BaseModel


class MaterialCreate(BaseModel):
    name: str
    category: str
    unit: str
    minimum_stock: int = 0


class MaterialResponse(MaterialCreate):
    id: int

    class Config:
        from_attributes = True
