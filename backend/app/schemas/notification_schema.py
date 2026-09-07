from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    title: str = "Notification"
    message: Optional[str] = ""
    recipient: str = "ALL"
    status: str = "Unread"


class NotificationResponse(NotificationCreate):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
