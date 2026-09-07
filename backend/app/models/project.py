from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_name = Column(
        String(200),
        nullable=False
    )

    # Unique code identifying the project
    project_code = Column(
        String(50),
        nullable=True
    )

    # Project category
    # Examples:
    # Residential
    # Commercial
    # Industrial
    # Infrastructure
    # Government
    project_category = Column(
        String(100),
        nullable=True
    )

    # Project priority
    # Examples:
    # Low
    # Medium
    # High
    # Critical
    priority = Column(
        String(50),
        nullable=True
    )

    description = Column(
        Text
    )

    location = Column(
        String(200)
    )

    start_date = Column(
        Date
    )

    end_date = Column(
        Date
    )

    budget = Column(
        Integer
    )

    status = Column(
        String(50),
        default="Planning"
    )

    # Project closure validation fields

    # All required inspections must be approved
    inspection_approved = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # All financial settlements must be completed
    financial_settlement_complete = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # All pending project issues must be resolved
    pending_issues_resolved = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # Client must accept the completed project
    client_accepted = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # Project Manager
    manager_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    manager = relationship(
        "User"
    )

    # Project milestones
    milestones = relationship(
        "ProjectMilestone",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Site Engineer assignments
    engineer_assignments = relationship(
        "ProjectEngineerAssignment",
        back_populates="project",
        cascade="all, delete-orphan"
    )
