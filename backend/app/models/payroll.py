from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Payroll(Base):
    __tablename__ = "payroll"

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

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=True,
        index=True
    )

    pay_rate = Column(
        Float,
        nullable=False,
        default=0.0
    )

    working_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    working_hours = Column(
        Float,
        nullable=False,
        default=0.0
    )

    overtime_hours = Column(
        Float,
        nullable=False,
        default=0.0
    )

    leave_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    estimated_pay = Column(
        Float,
        nullable=False,
        default=0.0
    )

    payroll_status = Column(
        String(50),
        nullable=False,
        default="PENDING"
    )

    worker = relationship(
        "Worker",
        back_populates="payrolls"
    )
