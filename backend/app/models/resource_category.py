from sqlalchemy import Column, Integer, String

from app.database.database import Base


class ResourceCategory(Base):
    __tablename__ = "resource_categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    description = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="Active"
    )