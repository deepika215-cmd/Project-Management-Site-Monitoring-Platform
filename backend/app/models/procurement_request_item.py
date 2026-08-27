from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ProcurementRequestItem(Base):
    __tablename__ = "procurement_request_items"

    id = Column(Integer, primary_key=True, index=True)

    procurement_request_id = Column(
        Integer,
        ForeignKey("procurement_requests.id"),
        nullable=False
    )

    item_name = Column(
        String(200),
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    estimated_unit_price = Column(
        Float,
        default=0
    )

    estimated_total_price = Column(
        Float,
        default=0
    )

    remarks = Column(String(500))

    procurement_request = relationship(
        "ProcurementRequest"
    )