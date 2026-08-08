from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    description = Column(String(500))

    report_type = Column(String(100))

    status = Column(String(100))