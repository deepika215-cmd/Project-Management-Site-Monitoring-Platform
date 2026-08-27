from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)

    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id"),
        nullable=False
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    procurement_request_id = Column(
        Integer,
        ForeignKey("procurement_requests.id"),
        nullable=False
    )

    order_date = Column(Date, nullable=False)

    expected_delivery_date = Column(Date)

    total_amount = Column(Float, default=0)

    tax_amount = Column(Float, default=0)

    additional_charges = Column(Float, default=0)

    overall_amount = Column(Float, default=0)

    status = Column(String(30), default="Processing")

    vendor = relationship("Vendor")

    project = relationship("Project")

    procurement_request = relationship("ProcurementRequest")
