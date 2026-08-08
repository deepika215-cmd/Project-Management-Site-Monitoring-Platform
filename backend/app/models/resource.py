from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    type = Column(String(100))

    # Total quantity of the resource
    quantity = Column(Integer, nullable=False, default=0)

    # Quantity currently allocated/used
    allocated_quantity = Column(Integer, nullable=False, default=0)

    status = Column(String(50), default="Available")

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")