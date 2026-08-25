from pydantic import BaseModel


class InventoryAnalytics(BaseModel):
    inventory_id: int
    item_name: str
    quantity: int
    used: int
    remaining: int