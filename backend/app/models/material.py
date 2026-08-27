from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True)

    category = Column(String(50), nullable=False)

    unit = Column(String(20), nullable=False)

    minimum_stock = Column(Integer, default=0)
