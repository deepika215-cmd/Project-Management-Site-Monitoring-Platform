from sqlalchemy import Column, Integer, String, ForeignKey
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

    date = Column(String(50), nullable=False)

    status = Column(String(50), nullable=False)

    # Used to track whether this attendance
    # record has been counted/processed
    used = Column(Integer, default=0)

    worker = relationship("Worker")