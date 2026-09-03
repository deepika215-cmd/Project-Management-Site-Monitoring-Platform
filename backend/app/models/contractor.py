from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    company_name = Column(
        String(200)
    )

    phone = Column(
        String(20)
    )

    email = Column(
        String(200)
    )

    status = Column(
        String(50),
        default="Active"
    )

    workers = relationship(
        "WorkerAssignment",
        back_populates="contractor"
    )