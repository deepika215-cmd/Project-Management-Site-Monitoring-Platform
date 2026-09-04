from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class DelayRecord(Base):
    __tablename__ = "delay_records"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    delay_date = Column(Date, nullable=False)

    reason = Column(String(500), nullable=False)

    duration_hours = Column(Integer, nullable=False)

    affected_work = Column(String(300))

    impact = Column(String(500))

    project = relationship("Project")