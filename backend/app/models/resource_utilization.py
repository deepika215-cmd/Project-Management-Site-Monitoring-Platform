from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ResourceUtilization(Base):
    __tablename__ = "resource_utilization"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

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

    usage_date = Column(
        Date,
        nullable=False
    )

    hours_used = Column(
        Float,
        nullable=False,
        default=0
    )

    status = Column(
        String(50),
        nullable=False,
        default="Used"
    )

    resource = relationship("Resource")
    project = relationship("Project")