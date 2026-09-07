from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.database import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True, index=True)
    expense_name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    description = Column(String(500), nullable=True)
    expense_date = Column(Date, nullable=True)
    payment_status = Column(String(50), nullable=False, default="Pending")
    supplier = Column(String(200), nullable=True)
    reference = Column(String(200), nullable=True)
    source_module = Column(String(100), nullable=True, default="MANUAL")
    category = relationship("BudgetCategory", back_populates="expenses")
    budget = relationship("Budget", back_populates="expenses")
    project = relationship("Project")
