from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class SiteActivityLog(Base):
    __tablename__ = "site_activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    activity_date = Column(Date, nullable=False)
    activity_time = Column(Time)
    activity_type = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    responsible_person = Column(String(200), nullable=False)

    project = relationship("Project")
