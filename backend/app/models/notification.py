from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    message = Column(String(500))

    recipient = Column(String(100))

    status = Column(String(50), default="Unread")