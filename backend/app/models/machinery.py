from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Machinery(Base):
    __tablename__ = "machinery"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    machinery_type = Column(String(100), nullable=False)

    location = Column(String(200))

    status = Column(String(50), default="Available")

    operator = Column(String(200))

    hours_used = Column(Float, default=0)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=True
    )

    project = relationship("Project")
