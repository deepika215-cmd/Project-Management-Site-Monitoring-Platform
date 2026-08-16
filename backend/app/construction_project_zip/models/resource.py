from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)

    resource_name = Column(String(100), nullable=False)

    resource_type = Column(String(50), nullable=False)

    quantity = Column(Integer, default=1)

    status = Column(String(50), default="Available")

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")