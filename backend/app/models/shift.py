from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    shift_name = Column(
        String(100),
        nullable=False
    )

    shift_date = Column(
        String(50),
        nullable=False
    )

    start_time = Column(
        String(20),
        nullable=False
    )

    end_time = Column(
        String(20),
        nullable=False
    )

    shift_type = Column(
        String(50),
        default="REGULAR"
    )

    status = Column(
        String(50),
        default="SCHEDULED"
    )

    remarks = Column(
        String(255),
        nullable=True
    )

    worker = relationship("Worker")

    project = relationship("Project")
