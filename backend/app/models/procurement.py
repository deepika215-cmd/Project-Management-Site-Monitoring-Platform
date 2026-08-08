from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Procurement(Base):
    __tablename__ = "procurement"

    id = Column(Integer, primary_key=True, index=True)

    item_name = Column(String(200), nullable=False)

    quantity = Column(Integer)

    supplier = Column(String(200))

    status = Column(String(100))

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")