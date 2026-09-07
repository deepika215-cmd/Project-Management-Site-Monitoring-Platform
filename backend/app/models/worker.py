from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    role = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(20)
    )

    email = Column(
        String(200)
    )

    # Workforce category
    # Examples:
    # Engineer
    # Supervisor
    # Contractor
    # Skilled Worker
    # Unskilled Worker
    # Consultant
    category = Column(
        String(100),
        nullable=False,
        default="Skilled Worker"
    )

    # Skill / work type
    skill_type = Column(
        String(150)
    )

    # Contractor responsible for the worker
    contractor_id = Column(
        Integer,
        nullable=True
    )

    # Joining date
    joining_date = Column(
        String(50)
    )

    # Active / Inactive
    status = Column(
        String(50),
        default="Active"
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    assignments = relationship(
        "WorkerAssignment",
        back_populates="worker",
        cascade="all, delete-orphan"
    )

    attendances = relationship(
        "Attendance",
        back_populates="worker",
        cascade="all, delete-orphan"
    )

    payrolls = relationship(
        "Payroll",
        back_populates="worker",
        cascade="all, delete-orphan"
    )
