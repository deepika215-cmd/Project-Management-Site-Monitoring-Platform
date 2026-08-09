from sqlalchemy import Column, Integer, String, Boolean

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    email = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    phone = Column(String(20), nullable=False)

    role = Column(String(50), nullable=False)

    is_active = Column(Boolean, default=True)