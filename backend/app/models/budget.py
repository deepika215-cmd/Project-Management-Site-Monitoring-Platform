from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.database import Base

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True, index=True)
    allocated_amount = Column(Float, nullable=False, default=0.0)
    description = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="Active")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    category = relationship("BudgetCategory", back_populates="budgets")
    project = relationship("Project")
    cost_estimates = relationship("CostEstimate", back_populates="budget")
    expenses = relationship("Expense", back_populates="budget")
