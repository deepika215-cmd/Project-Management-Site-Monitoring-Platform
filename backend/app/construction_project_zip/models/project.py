from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Float
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

    completion_percentage = Column(Float, default=0.0)

    manager_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    manager = relationship("User")