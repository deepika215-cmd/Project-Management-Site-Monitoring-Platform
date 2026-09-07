from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    file_type = Column(
        String(100),
        nullable=True
    )

    file_size = Column(
        Integer,
        nullable=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=True
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    project = relationship(
        "Project"
    )

    uploader = relationship(
        "User"
    )