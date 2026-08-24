from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False
    )

    project_id = Column(
        Integer,
        nullable=True
    )

    date = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    check_in_time = Column(
        String(20),
        nullable=True
    )

    check_out_time = Column(
        String(20),
        nullable=True
    )

    working_hours = Column(
        Float,
        default=0.0
    )

    remarks = Column(
        String(255),
        nullable=True
    )

    # Used to track whether this attendance
    # record has been counted/processed
    used = Column(
        Integer,
        default=0
    )

    worker = relationship(
    "Worker",
    back_populates="attendances"
)