from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class WorkerAssignment(Base):
    __tablename__ = "worker_assignments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False,
        index=True
    )

    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id"),
        nullable=False,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    work_activity = Column(
        String(200)
    )

    assignment_start_date = Column(
        String(50),
        nullable=False
    )

    assignment_end_date = Column(
        String(50)
    )

    assignment_status = Column(
        String(50),
        default="ACTIVE"
    )

    worker = relationship(
        "Worker",
        back_populates="assignments"
    )

    contractor = relationship(
        "Contractor",
        back_populates="workers"
    )