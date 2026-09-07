from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.database import Base

class CostEstimate(Base):
    __tablename__ = "cost_estimates"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=True, index=True)
    item_name = Column(String(200), nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    unit = Column(String(50), nullable=True)
    unit_cost = Column(Float, nullable=False, default=0.0)
    estimated_amount = Column(Float, nullable=False, default=0.0)
    description = Column(String(500), nullable=True)
    estimate_date = Column(Date, nullable=True)
    category = relationship("BudgetCategory", back_populates="cost_estimates")
    budget = relationship("Budget", back_populates="cost_estimates")
    project = relationship("Project")
