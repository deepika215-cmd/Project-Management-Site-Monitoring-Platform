from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class DailyProgress(Base):
    __tablename__ = "daily_progress"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("projects.id"))

    report_date = Column(Date)

    work_category = Column(String)

    activity = Column(String)

    completion_percentage = Column(Float)

    contractor_name = Column(String)

    workers_present = Column(Integer)

    workers_absent = Column(Integer)

    machinery_used = Column(String)

    materials_used = Column(String)

    weather = Column(String)

    safety_observation = Column(Text)

    quality_remarks = Column(Text)

    delay_hours = Column(Float)

    delay_reason = Column(Text)

    comments = Column(Text)

    project = relationship("Project")