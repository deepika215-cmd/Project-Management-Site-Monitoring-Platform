from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    phone = Column(String(15))

    designation = Column(String(50))

    salary = Column(Integer)

    status = Column(String(30), default="Active")

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")