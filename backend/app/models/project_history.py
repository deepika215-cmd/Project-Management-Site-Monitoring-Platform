from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class ProjectHistory(Base):
    __tablename__ = "project_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    action = Column(
        String(100),
        nullable=False
    )

    field_name = Column(
        String(100),
        nullable=True
    )

    old_value = Column(
        Text,
        nullable=True
    )

    new_value = Column(
        Text,
        nullable=True
    )

    changed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    project = relationship("Project")

    user = relationship("User")