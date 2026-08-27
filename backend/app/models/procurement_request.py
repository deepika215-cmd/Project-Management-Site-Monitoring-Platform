from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    requested_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    item_name = Column(String(200), nullable=False)

    category = Column(String(100), nullable=False)

    quantity = Column(Integer, nullable=False)

    required_date = Column(Date, nullable=False)

    purpose = Column(String(500), nullable=False)

    priority = Column(String(30), default="NORMAL")

    request_date = Column(Date, nullable=False)

    status = Column(String(30), default="Pending")

    remarks = Column(String(500))

    project = relationship("Project")

    requester = relationship("User")
