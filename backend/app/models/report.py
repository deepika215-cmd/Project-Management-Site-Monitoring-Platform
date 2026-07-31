from sqlalchemy import Column, Integer, String, Date
from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    report_name = Column(String(100), nullable=False)

    report_type = Column(String(50))

    generated_date = Column(Date)

    generated_by = Column(String(100))

    file_path = Column(String(255))