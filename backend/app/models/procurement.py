from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Procurement(Base):
    __tablename__ = "procurements"

    id = Column(Integer, primary_key=True, index=True)

    item_name = Column(String(100), nullable=False)

    quantity = Column(Integer, nullable=False)

    supplier = Column(String(100))

    order_date = Column(Date)

    expected_delivery = Column(Date)

    status = Column(String(50), default="Ordered")

    project_id = Column(
        Integer,
        ForeignKey("projects.id")
    )

    project = relationship("Project")