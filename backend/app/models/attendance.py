from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    attendance_date = Column(Date, nullable=False)

    status = Column(String(20), default="Present")

    check_in = Column(String(20))

    check_out = Column(String(20))

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    worker = relationship("Worker")