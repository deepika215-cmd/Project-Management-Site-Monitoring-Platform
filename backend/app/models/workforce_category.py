from sqlalchemy import Column, Integer, String, Text

from app.database.database import Base


class WorkforceCategory(Base):
    __tablename__ = "workforce_categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="Active"
    )