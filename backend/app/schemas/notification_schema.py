from pydantic import BaseModel


class NotificationCreate(BaseModel):
    title: str
    message: str
    recipient: str
    status: str


class NotificationResponse(NotificationCreate):
    id: int

    class Config:
        from_attributes = True