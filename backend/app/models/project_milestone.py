from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProjectMilestone(Base):

    __tablename__ = "project_milestones"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(String(500))

    due_date = Column(Date)

    status = Column(String(50), default="Pending")

    completion_percentage = Column(Float, default=0.0)

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")