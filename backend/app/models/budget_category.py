from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    budgets = relationship(
        "Budget",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    cost_estimates = relationship(
        "CostEstimate",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    expenses = relationship(
        "Expense",
        back_populates="category",
        cascade="all, delete-orphan",
    )