from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class ProgressPhoto(Base):
    __tablename__ = "progress_photos"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    daily_progress_id = Column(
        Integer,
        ForeignKey("daily_progress.id"),
        nullable=True
    )

    photo_url = Column(String(500), nullable=False)

    description = Column(String(500))

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    project = relationship("Project")
