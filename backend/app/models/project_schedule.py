from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey

from app.database.database import Base


class ProjectScheduleActivity(Base):
    __tablename__ = "project_schedule_activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    activity_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    dependency = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="Not Started")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
