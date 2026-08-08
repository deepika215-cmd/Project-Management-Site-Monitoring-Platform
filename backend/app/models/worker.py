from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    role = Column(String(100))

    phone = Column(String(20))

    address = Column(String(300))

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")