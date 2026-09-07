from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    item_name = Column(String(100), nullable=False)

    category = Column(String(50), nullable=False)

    quantity = Column(Integer, default=0)

    unit = Column(String(20))

    supplier = Column(String(100))

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    resource_id = Column(
        Integer,
        ForeignKey("resources.id"),
        nullable=True
    )

    project = relationship("Project")

    resource = relationship("Resource")