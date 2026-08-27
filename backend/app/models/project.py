from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    project_name = Column(String(200), nullable=False)

    description = Column(Text)

    location = Column(String(200))

    start_date = Column(Date)

    end_date = Column(Date)

    budget = Column(Integer)

    status = Column(String(50), default="Planning")

    manager_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    manager = relationship("User")

    milestones = relationship(
        "ProjectMilestone",
        back_populates="project",
        cascade="all, delete-orphan"
    )