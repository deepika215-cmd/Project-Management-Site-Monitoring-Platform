from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, default="Notification")
    message = Column(String(500), default="")
    recipient = Column(String(100), default="ALL")
    status = Column(String(50), default="Unread")
    created_at = Column(DateTime, default=datetime.utcnow)
