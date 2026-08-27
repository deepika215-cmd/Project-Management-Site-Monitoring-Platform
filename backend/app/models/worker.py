from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    role = Column(String(100), nullable=False)

    phone = Column(String(20))

    email = Column(String(200))

    status = Column(String(100), default="Active")