from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    worker_id = Column(Integer, ForeignKey("workers.id"))

    date = Column(String(50))

    status = Column(String(50))

    worker = relationship("Worker")