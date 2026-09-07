from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)

    resource_id = Column(
        Integer,
        ForeignKey("resources.id"),
        nullable=False,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=True,
        index=True
    )

    quantity = Column(Integer, nullable=False)

    allocation_date = Column(
        Date,
        nullable=False
    )

    expected_return_date = Column(
        Date,
        nullable=False
    )

    actual_return_date = Column(
        Date,
        nullable=True
    )

    responsible_person = Column(
        String(200),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="Allocated"
    )

    resource = relationship("Resource")

    project = relationship("Project")

    worker = relationship("Worker")