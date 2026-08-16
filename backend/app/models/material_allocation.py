from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class MaterialAllocation(Base):
    __tablename__ = "material_allocations"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    material_id = Column(
        Integer,
        ForeignKey("materials.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)

    allocation_date = Column(Date, nullable=False)

    work_activity = Column(String(200), nullable=False)

    responsible_user = Column(String(100))

    status = Column(
        String(30),
        default="ALLOCATED"
    )

    project = relationship("Project")

    material = relationship("Material")