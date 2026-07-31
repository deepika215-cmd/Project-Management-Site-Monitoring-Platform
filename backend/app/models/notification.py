from sqlalchemy import Column, Integer, String, DateTime
from app.database.database import Base
import datetime


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(100), nullable=False)

    message = Column(String(500), nullable=False)

    notification_type = Column(String(50))

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )