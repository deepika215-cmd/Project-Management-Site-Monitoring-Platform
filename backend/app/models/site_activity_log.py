from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class SiteActivityLog(Base):
    __tablename__ = "site_activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    activity_date = Column(Date, nullable=False)

    activity_time = Column(Time, nullable=False)

    activity_type = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    responsible_person = Column(
        String(200),
        nullable=False
    )

    project = relationship("Project")