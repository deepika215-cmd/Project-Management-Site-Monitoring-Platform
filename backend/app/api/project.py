
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.auth import get_current_user

from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.project_history import ProjectHistory
from app.models.daily_progress import DailyProgress
from app.models.user import User
from app.models.payroll import Payroll

from app.schemas.project_schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatusUpdate,
    ProjectClosureUpdate
)

from app.schemas.project_tracking import ProjectTrackingResponse

from app.schemas.project_history import ProjectHistoryResponse


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# ---------------------------------------------------------
# Create Project
# ---------------------------------------------------------

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # Only ADMIN can create projects
    # -----------------------------------------------------

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN can create projects"
        )

    # -----------------------------------------------------
    # Validate project dates
    # -----------------------------------------------------

    if project.end_date < project.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # -----------------------------------------------------
    # Validate budget
    # -----------------------------------------------------

    if project.budget < 0:
        raise HTTPException(
            status_code=400,
            detail="Budget cannot be negative"
        )

    # -----------------------------------------------------
    # Validate project code uniqueness
    # -----------------------------------------------------

    existing_project = db.query(Project).filter(
        Project.project_code == project.project_code
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project code already exists"
        )

    # -----------------------------------------------------
    # Validate Project Manager
    # -----------------------------------------------------

    manager = db.query(User).filter(
        User.id == project.manager_id
    ).first()

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Project Manager not found"
        )

    if manager.role != "MANAGER":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a MANAGER"
        )

    # -----------------------------------------------------
    # Create project
    # -----------------------------------------------------
    # New projects must always start in Planning.
    # Ignore any status sent by the client.

    new_project = Project(
        project_name=project.project_name,
        project_code=project.project_code,
        project_category=project.project_category,
        description=project.description,
        location=project.location,
        start_date=project.start_date,
        end_date=project.end_date,
        budget=project.budget,
        priority=project.priority,
        status="Planning",
        manager_id=project.manager_id,

        # Closure conditions start as incomplete
        inspection_approved=False,
        financial_settlement_complete=False,
        pending_issues_resolved=False,
        client_accepted=False
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # -----------------------------------------------------
    # Record project creation in history
    # -----------------------------------------------------

    history = ProjectHistory(
        project_id=new_project.id,
        changed_by=current_user.id,
        action="PROJECT_CREATED",
        field_name=None,
        old_value=None,
        new_value="Project created with Planning status"
    )

    db.add(history)
    db.commit()

    return new_project


# ---------------------------------------------------------
# Get All Projects
# ---------------------------------------------------------

@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db)
):

    return db.query(Project).all()


# ---------------------------------------------------------
# Project Tracking
# ---------------------------------------------------------

@router.get(
    "/{project_id}/tracking",
    response_model=ProjectTrackingResponse
)
def get_project_tracking(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Milestone information
    # -----------------------------------------------------

    milestones = db.query(ProjectMilestone).filter(
        ProjectMilestone.project_id == project_id
    ).all()

    total_milestones = len(milestones)

    completed_milestones = len([
        milestone
        for milestone in milestones
        if milestone.status == "Completed"
    ])

    pending_milestones = (
        total_milestones - completed_milestones
    )

    # -----------------------------------------------------
    # Actual construction progress
    #
    # Progress is calculated from the latest Daily Progress
    # record for each work category.
    # -----------------------------------------------------

    daily_progress_records = (
        db.query(DailyProgress)
        .filter(
            DailyProgress.project_id == project_id
        )
        .order_by(
            DailyProgress.report_date.asc(),
            DailyProgress.id.asc()
        )
        .all()
    )

    latest_progress_by_category = {}

    for record in daily_progress_records:

        category = record.work_category

        latest_progress_by_category[category] = (
            record.completion_percentage
        )

    progress = 0

    if latest_progress_by_category:

        progress = round(
            sum(latest_progress_by_category.values())
            / len(latest_progress_by_category),
            2
        )

    return {
        "project_id": project.id,
        "project_name": project.project_name,
        "status": project.status,
        "total_milestones": total_milestones,
        "completed_milestones": completed_milestones,
        "pending_milestones": pending_milestones,
        "progress": progress
    }


# ---------------------------------------------------------
# Budget & Cost Integration
# ---------------------------------------------------------

@router.get("/{project_id}/budget-cost")
def get_project_budget_cost(
    project_id: int,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Find project
    # -----------------------------------------------------

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Project Budget
    # -----------------------------------------------------

    budget = project.budget or 0

    # -----------------------------------------------------
    # Calculate Actual Labour Cost
    #
    # Payroll records are connected to projects using
    # project_id.
    #
    # estimated_pay is calculated by the Payroll API.
    # -----------------------------------------------------

    payroll_records = db.query(Payroll).filter(
        Payroll.project_id == project_id
    ).all()

    actual_labour_cost = round(
        sum(
            payroll.estimated_pay or 0
            for payroll in payroll_records
        ),
        2
    )

    # -----------------------------------------------------
    # Material Cost
    #
    # Current Inventory / Material models do not contain
    # price or cost information.
    #
    # Therefore we do not invent a material cost.
    # -----------------------------------------------------

    actual_material_cost = 0.0

    # -----------------------------------------------------
    # Procurement Cost
    #
    # Current Procurement model does not contain price,
    # unit cost, or total cost.
    #
    # Therefore procurement cost cannot be calculated yet.
    # -----------------------------------------------------

    actual_procurement_cost = 0.0

    # -----------------------------------------------------
    # Total Actual Cost
    # -----------------------------------------------------

    total_actual_cost = round(
        actual_labour_cost
        + actual_material_cost
        + actual_procurement_cost,
        2
    )

    # -----------------------------------------------------
    # Remaining Budget
    # -----------------------------------------------------

    remaining_budget = round(
        budget - total_actual_cost,
        2
    )

    # -----------------------------------------------------
    # Budget Utilization Percentage
    # -----------------------------------------------------

    budget_utilization_percentage = 0.0

    if budget > 0:

        budget_utilization_percentage = round(
            (total_actual_cost / budget) * 100,
            2
        )

    # -----------------------------------------------------
    # Return Budget & Cost Summary
    # -----------------------------------------------------

    return {
        "project_id": project.id,
        "project_name": project.project_name,
        "budget": budget,
        "actual_labour_cost": actual_labour_cost,
        "actual_material_cost": actual_material_cost,
        "actual_procurement_cost": actual_procurement_cost,
        "total_actual_cost": total_actual_cost,
        "remaining_budget": remaining_budget,
        "budget_utilization_percentage":
            budget_utilization_percentage
    }


# ---------------------------------------------------------
# Get Project By ID
# ---------------------------------------------------------

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


# ---------------------------------------------------------
# Update Project
# ---------------------------------------------------------

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Closed projects cannot be modified
    # -----------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can update projects"
        )

    # -----------------------------------------------------
    # Validate dates
    # -----------------------------------------------------

    if project_data.end_date < project_data.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # -----------------------------------------------------
    # Validate budget
    # -----------------------------------------------------

    if project_data.budget < 0:
        raise HTTPException(
            status_code=400,
            detail="Budget cannot be negative"
        )

    # -----------------------------------------------------
    # Validate project code uniqueness
    # -----------------------------------------------------

    existing_project = db.query(Project).filter(
        Project.project_code == project_data.project_code,
        Project.id != project_id
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project code already exists"
        )

    # -----------------------------------------------------
    # Validate Project Manager
    # -----------------------------------------------------

    manager = db.query(User).filter(
        User.id == project_data.manager_id
    ).first()

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Project Manager not found"
        )

    if manager.role != "MANAGER":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a MANAGER"
        )

    # -----------------------------------------------------
    # Record changes before updating
    # -----------------------------------------------------

    fields_to_check = [
        "project_name",
        "project_code",
        "project_category",
        "description",
        "location",
        "start_date",
        "end_date",
        "budget",
        "priority",
        "manager_id"
    ]

    new_values = {
        "project_name": project_data.project_name,
        "project_code": project_data.project_code,
        "project_category": project_data.project_category,
        "description": project_data.description,
        "location": project_data.location,
        "start_date": project_data.start_date,
        "end_date": project_data.end_date,
        "budget": project_data.budget,
        "priority": project_data.priority,
        "manager_id": project_data.manager_id
    }

    for field in fields_to_check:

        old_value = getattr(project, field)
        new_value = new_values[field]

        if old_value != new_value:

            history = ProjectHistory(
                project_id=project.id,
                changed_by=current_user.id,
                action="UPDATE",
                field_name=field,
                old_value=(
                    str(old_value)
                    if old_value is not None
                    else None
                ),
                new_value=(
                    str(new_value)
                    if new_value is not None
                    else None
                )
            )

            db.add(history)

    # -----------------------------------------------------
    # Update fields
    # -----------------------------------------------------
    # Status and closure conditions are intentionally NOT
    # updated here.

    project.project_name = project_data.project_name
    project.project_code = project_data.project_code
    project.project_category = project_data.project_category
    project.description = project_data.description
    project.location = project_data.location
    project.start_date = project_data.start_date
    project.end_date = project_data.end_date
    project.budget = project_data.budget
    project.priority = project_data.priority
    project.manager_id = project_data.manager_id

    db.commit()
    db.refresh(project)

    return project


# ---------------------------------------------------------
# Update Project Status
# ---------------------------------------------------------

@router.put(
    "/{project_id}/status",
    response_model=ProjectResponse
)
def update_project_status(
    project_id: int,
    status_data: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    current_status = project.status
    new_status = status_data.status

    # -----------------------------------------------------
    # Only ADMIN or MANAGER can change project status
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can change project status"
        )

    # -----------------------------------------------------
    # Closed projects cannot be modified
    # -----------------------------------------------------

    if current_status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # -----------------------------------------------------
    # Valid status flow
    # -----------------------------------------------------

    allowed_transitions = {

        "Planning": [
            "In Progress"
        ],

        "In Progress": [
            "On Hold",
            "Completed"
        ],

        "On Hold": [
            "In Progress"
        ],

        "Completed": [
            "Closed"
        ],

        "Closed": []
    }

    allowed_statuses = allowed_transitions.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    # -----------------------------------------------------
    # Record status change
    # -----------------------------------------------------

    history = ProjectHistory(
        project_id=project.id,
        changed_by=current_user.id,
        action="STATUS_CHANGE",
        field_name="status",
        old_value=current_status,
        new_value=new_status
    )

    db.add(history)

    # -----------------------------------------------------
    # Update status
    # -----------------------------------------------------

    project.status = new_status

    db.commit()
    db.refresh(project)

    return project


# ---------------------------------------------------------
# Update Project Closure Conditions
# ---------------------------------------------------------

@router.put(
    "/{project_id}/closure-validation",
    response_model=ProjectResponse
)
def update_project_closure_validation(
    project_id: int,
    closure_data: ProjectClosureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Closed projects cannot be modified
    # -----------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail=(
                "Only ADMIN or MANAGER can update "
                "project closure conditions"
            )
        )

    # -----------------------------------------------------
    # Record closure-condition changes
    # -----------------------------------------------------

    closure_fields = [
        "inspection_approved",
        "financial_settlement_complete",
        "pending_issues_resolved",
        "client_accepted"
    ]

    new_values = {
        "inspection_approved":
            closure_data.inspection_approved,

        "financial_settlement_complete":
            closure_data.financial_settlement_complete,

        "pending_issues_resolved":
            closure_data.pending_issues_resolved,

        "client_accepted":
            closure_data.client_accepted
    }

    for field in closure_fields:

        old_value = getattr(project, field)
        new_value = new_values[field]

        if old_value != new_value:

            history = ProjectHistory(
                project_id=project.id,
                changed_by=current_user.id,
                action="CLOSURE_VALIDATION_UPDATE",
                field_name=field,
                old_value=str(old_value),
                new_value=str(new_value)
            )

            db.add(history)

            setattr(
                project,
                field,
                new_value
            )

    db.commit()
    db.refresh(project)

    return project


# ---------------------------------------------------------
# Close Project
# ---------------------------------------------------------

@router.put(
    "/{project_id}/close",
    response_model=ProjectResponse
)
def close_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Only ADMIN or MANAGER can close projects
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can close projects"
        )

    # -----------------------------------------------------
    # Already closed
    # -----------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Project is already closed"
        )

    # -----------------------------------------------------
    # Project must be completed first
    # -----------------------------------------------------

    if project.status != "Completed":
        raise HTTPException(
            status_code=400,
            detail="Only completed projects can be closed"
        )

    # -----------------------------------------------------
    # Validate all project milestones
    # -----------------------------------------------------

    milestones = db.query(ProjectMilestone).filter(
        ProjectMilestone.project_id == project_id
    ).all()

    incomplete_milestones = [
        milestone
        for milestone in milestones
        if milestone.status != "Completed"
    ]

    if incomplete_milestones:
        raise HTTPException(
            status_code=400,
            detail=(
                "Project cannot be closed because "
                "all milestones are not completed"
            )
        )

    # -----------------------------------------------------
    # Validate inspection approval
    # -----------------------------------------------------

    if not project.inspection_approved:
        raise HTTPException(
            status_code=400,
            detail="Project cannot be closed because inspection is not approved"
        )

    # -----------------------------------------------------
    # Validate financial settlement
    # -----------------------------------------------------

    if not project.financial_settlement_complete:
        raise HTTPException(
            status_code=400,
            detail=(
                "Project cannot be closed because "
                "financial settlement is not complete"
            )
        )

    # -----------------------------------------------------
    # Validate pending issues
    # -----------------------------------------------------

    if not project.pending_issues_resolved:
        raise HTTPException(
            status_code=400,
            detail=(
                "Project cannot be closed because "
                "pending issues are not resolved"
            )
        )

    # -----------------------------------------------------
    # Validate client acceptance
    # -----------------------------------------------------

    if not project.client_accepted:
        raise HTTPException(
            status_code=400,
            detail=(
                "Project cannot be closed because "
                "client acceptance has not been received"
            )
        )

    # -----------------------------------------------------
    # Record project closure
    # -----------------------------------------------------

    history = ProjectHistory(
        project_id=project.id,
        changed_by=current_user.id,
        action="PROJECT_CLOSED",
        field_name="status",
        old_value="Completed",
        new_value="Closed"
    )

    db.add(history)

    # -----------------------------------------------------
    # Close project
    # -----------------------------------------------------

    project.status = "Closed"

    db.commit()
    db.refresh(project)

    return project


# ---------------------------------------------------------
# Get Project History
# ---------------------------------------------------------

@router.get(
    "/{project_id}/history",
    response_model=list[ProjectHistoryResponse]
)
def get_project_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Only authorized users can view project history
    # -----------------------------------------------------

    if current_user.role not in [
        "ADMIN",
        "MANAGER",
        "ENGINEER"
    ]:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view project history"
        )

    # -----------------------------------------------------
    # Get history
    # -----------------------------------------------------

    history = db.query(
        ProjectHistory
    ).filter(
        ProjectHistory.project_id == project_id
    ).order_by(
        ProjectHistory.changed_at.desc()
    ).all()

    return history


# ---------------------------------------------------------
# Delete Project
# ---------------------------------------------------------

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Only ADMIN can delete projects
    # -----------------------------------------------------

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN can delete projects"
        )

    # -----------------------------------------------------
    # Closed projects cannot be deleted
    # -----------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be deleted"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }