from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProjectMilestone(Base):
    __tablename__ = "project_milestones"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(String(500))

    due_date = Column(Date)

    status = Column(String(50), default="Pending")

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")