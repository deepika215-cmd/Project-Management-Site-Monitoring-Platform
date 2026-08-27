from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(
        String(100),
        nullable=False,
        unique=True
    )

    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id"),
        nullable=False
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=False
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    invoice_date = Column(Date, nullable=False)

    due_date = Column(Date)

    invoice_amount = Column(Float, nullable=False)

    payment_status = Column(
        String(30),
        default="Pending"
    )

    invoice_status = Column(
        String(30),
        default="Received"
    )

    remarks = Column(String(500))

    vendor = relationship("Vendor")

    purchase_order = relationship("PurchaseOrder")

    project = relationship("Project")
