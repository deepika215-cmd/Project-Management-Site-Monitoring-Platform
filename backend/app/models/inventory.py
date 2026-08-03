from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    material_name = Column(String(200), nullable=False)

    quantity = Column(Integer)

    unit = Column(String(50))

    supplier = Column(String(200))

    status = Column(String(100))