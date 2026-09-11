from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    title: str = "Notification"
    message: Optional[str] = ""
    recipient: str = "ALL"
    recipient_user_id: Optional[int] = None
    notification_type: str = "SYSTEM"
    project_id: Optional[int] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    action_url: Optional[str] = None
    status: str = "Unread"


class NotificationResponse(NotificationCreate):
    id: int
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True
