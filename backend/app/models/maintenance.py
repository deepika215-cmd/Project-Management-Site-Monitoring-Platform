from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)

    machinery_id = Column(
        Integer,
        ForeignKey("machinery.id"),
        nullable=False
    )

    maintenance_type = Column(String(100), nullable=False)

    description = Column(String(500))

    scheduled_date = Column(Date, nullable=False)

    completion_date = Column(Date, nullable=True)

    status = Column(
        String(50),
        default="Scheduled"
    )

    cost = Column(
        Float,
        default=0
    )

    technician = Column(String(200))

    machinery = relationship("Machinery")
