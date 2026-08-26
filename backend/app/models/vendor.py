from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    vendor_name = Column(String(200), nullable=False, unique=True)

    contact_person = Column(String(100))

    contact_number = Column(String(30))

    email = Column(String(150))

    address = Column(String(300))

    category = Column(String(100), nullable=False)

    products_services = Column(String(500))

    status = Column(String(30), default="ACTIVE")
