from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class WeeklyProgress(Base):
    __tablename__ = "weekly_progress"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
    Integer,
    ForeignKey("projects.id"),
    nullable=False
)

    week_start = Column(Date)
    week_end = Column(Date)
    work_completed = Column(String)
    completion_percentage = Column(Float)
    worker_hours = Column(Integer)
    major_activities = Column(String)
    delays = Column(String)
    safety_incidents = Column(String)
    overall_status = Column(String)

    project = relationship("Project")