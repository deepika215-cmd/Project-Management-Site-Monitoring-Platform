from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.auth import get_current_user
from app.core.permissions import role_required

from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.project_history import ProjectHistory
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.daily_progress import DailyProgress
from app.models.user import User
from app.models.payroll import Payroll
from app.models.maintenance import Maintenance
from app.models.machinery import Machinery
from app.models.notification import Notification
from app.models.contractor import Contractor

from app.schemas.project_schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatusUpdate,
    ProjectClosureUpdate
)

from app.schemas.project_tracking import ProjectTrackingResponse

from app.schemas.project_history import ProjectHistoryResponse

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# =========================================================
# HELPER: GET PROJECT NOTIFICATION RECIPIENTS
# =========================================================

def get_project_notification_recipients(
    db: Session,
    project_id: int
):
    """
    Get notification recipients for a project.

    Recipients:
    - Project Manager
    - Assigned active Site Engineers

    Returns a set of email addresses so duplicate
    recipients are automatically removed.
    """

    recipients = set()

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return recipients

    # -----------------------------------------------------
    # Project Manager
    # -----------------------------------------------------

    if project.manager_id:

        manager = (
            db.query(User)
            .filter(
                User.id == project.manager_id,
                User.role == "PROJECT_MANAGER",
                User.is_active == True
            )
            .first()
        )

        if manager and manager.email:
            recipients.add(manager.email)

    # -----------------------------------------------------
    # Assigned Site Engineers
    # -----------------------------------------------------

    assignments = (
        db.query(ProjectEngineerAssignment)
        .filter(
            ProjectEngineerAssignment.project_id == project_id
        )
        .all()
    )

    for assignment in assignments:

        engineer = (
            db.query(User)
            .filter(
                User.id == assignment.engineer_id,
                User.role == "SITE_ENGINEER",
                User.is_active == True
            )
            .first()
        )

        if engineer and engineer.email:
            recipients.add(engineer.email)

    # -----------------------------------------------------
    # Contractor assigned to this project
    # -----------------------------------------------------
    contractors = db.query(Contractor).filter(
        Contractor.project_id == project_id,
        Contractor.status.in_(["Active", "ACTIVE", "active"]),
    ).all()
    contractor_emails = [c.email for c in contractors if c.email]
    if contractor_emails:
        contractor_users = db.query(User).filter(
            User.email.in_(contractor_emails),
            User.is_active == True,
        ).all()
        for contractor_user in contractor_users:
            recipients.add(contractor_user.email)

    return recipients


# =========================================================
# CREATE PROJECT
# =========================================================

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ADMIN, Project Managers and Site Engineers can create projects.
    # Project Managers are always assigned to projects they create.
    if current_user.role not in ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN, Project Manager or Site Engineer can create projects"
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
    # Resolve / validate project code
    # -----------------------------------------------------

    # Older frontend forms did not send project_code.  Keep those forms
    # compatible by generating a stable unique code on the backend.
    project_code = (project.project_code or "").strip()
    if not project_code:
        latest_id = db.query(Project.id).order_by(Project.id.desc()).first()
        next_number = (latest_id[0] if latest_id else 0) + 1
        project_code = f"BT-{next_number:04d}"
        while db.query(Project).filter(Project.project_code == project_code).first():
            next_number += 1
            project_code = f"BT-{next_number:04d}"

    existing_project = db.query(Project).filter(
        Project.project_code == project_code
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project code already exists"
        )

    # -----------------------------------------------------
    # Validate / resolve Project Manager
    # -----------------------------------------------------

    manager_id = project.manager_id
    if current_user.role == "PROJECT_MANAGER":
        manager_id = current_user.id

    manager = db.query(User).filter(
        User.id == manager_id
    ).first()

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Project Manager not found"
        )

    if manager.role != "PROJECT_MANAGER":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a MANAGER"
        )

    # -----------------------------------------------------
    # Create project
    # -----------------------------------------------------

    new_project = Project(
        project_name=project.project_name,
        project_code=project_code,
        project_category=project.project_category,
        description=project.description,
        location=project.location,
        start_date=project.start_date,
        end_date=project.end_date,
        budget=project.budget,
        priority=project.priority,
        status=project.status,
        manager_id=manager_id,

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


# =========================================================
# GET ALL PROJECTS
# =========================================================

@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "ADMIN":
        return db.query(Project).all()

    if current_user.role == "PROJECT_MANAGER":
        return db.query(Project).filter(Project.manager_id == current_user.id).all()

    if current_user.role == "SITE_ENGINEER":
        assigned_ids = [
            row.project_id
            for row in db.query(ProjectEngineerAssignment).filter(
                ProjectEngineerAssignment.engineer_id == current_user.id
            ).all()
        ]
        if not assigned_ids:
            return []
        return db.query(Project).filter(Project.id.in_(assigned_ids)).all()

    # Contractor and Client project relationships are not represented by a
    # dedicated assignment table in the current schema, so read-only access
    # falls back to the project catalogue.
    if current_user.role in ["CONTRACTOR", "CLIENT"]:
        return db.query(Project).all()

    return []


# =========================================================
# AVAILABLE PROJECT MANAGERS
# =========================================================

@router.get("/available-managers")
def get_available_project_managers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER"]:
        raise HTTPException(status_code=403, detail="Access denied")

    managers = (
        db.query(User)
        .filter(User.role == "PROJECT_MANAGER", User.is_active == True)
        .order_by(User.name.asc())
        .all()
    )

    return [
        {
            "id": manager.id,
            "name": manager.name,
            "full_name": manager.name,
            "email": manager.email,
            "role": manager.role,
            "is_active": manager.is_active,
        }
        for manager in managers
    ]


# =========================================================
# PROJECT DEADLINE NOTIFICATIONS
# =========================================================

@router.get("/deadline-notifications", dependencies=[Depends(role_required(["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER"]))])
def generate_project_deadline_notifications(
    db: Session = Depends(get_db)
):

    today = date.today()

    projects = (
        db.query(Project)
        .all()
    )

    notifications_created = 0
    upcoming_count = 0
    missed_count = 0

    # -----------------------------------------------------
    # Process each project
    # -----------------------------------------------------

    for project in projects:

        if not project.end_date:
            continue

        if project.status in ["Completed", "Closed"]:
            continue

        days_remaining = (
            project.end_date - today
        ).days

        notification_title = None
        notification_message = None

        # =================================================
        # MISSED PROJECT DEADLINE
        # =================================================

        if days_remaining < 0:

            notification_title = "Project Deadline Missed"

            notification_message = (
                f"Project #{project.id} - "
                f"{project.project_name} was due on "
                f"{project.end_date} and has not been completed."
            )

            missed_count += 1

        # =================================================
        # UPCOMING PROJECT DEADLINE
        # =================================================

        elif days_remaining <= 7:

            notification_title = (
                "Project Deadline Approaching"
            )

            if days_remaining == 0:
                deadline_text = "today"

            elif days_remaining == 1:
                deadline_text = "tomorrow"

            else:
                deadline_text = (
                    f"in {days_remaining} days"
                )

            notification_message = (
                f"Project #{project.id} - "
                f"{project.project_name} is due "
                f"{deadline_text} on {project.end_date}."
            )

            upcoming_count += 1

        else:
            continue

        # =================================================
        # GET PROJECT USERS
        # =================================================

        recipients = get_project_notification_recipients(
            db=db,
            project_id=project.id
        )

        # =================================================
        # CREATE NOTIFICATIONS
        # =================================================

        for recipient in recipients:

            existing_notification = (
                db.query(Notification)
                .filter(
                    Notification.title == notification_title,
                    Notification.message == notification_message,
                    Notification.recipient == recipient
                )
                .first()
            )

            if existing_notification:
                continue

            recipient_user = db.query(User).filter(User.email == recipient).first()
            notification = Notification(
                title=notification_title,
                message=notification_message,
                recipient=recipient,
                recipient_user_id=recipient_user.id if recipient_user else None,
                notification_type="DEADLINE",
                project_id=project.id,
                related_entity_type="PROJECT",
                related_entity_id=project.id,
                action_url=f"/projects/project-details/{project.id}",
                status="Unread"
            )

            db.add(notification)

            notifications_created += 1

    db.commit()

    return {
        "message": (
            "Project deadline notifications "
            "processed successfully"
        ),
        "today": today,
        "upcoming_projects": upcoming_count,
        "missed_projects": missed_count,
        "notifications_created": notifications_created
    }


# =========================================================
# PROJECT TRACKING
# =========================================================

@router.get(
    "/{project_id}/tracking",
    response_model=ProjectTrackingResponse,
    dependencies=[Depends(role_required(["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "CLIENT"]))]
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


# =========================================================
# BUDGET & COST INTEGRATION
# =========================================================

@router.get("/{project_id}/budget-cost", dependencies=[Depends(role_required(["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CLIENT"]))])
def get_project_budget_cost(
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
    # Project budget
    # -----------------------------------------------------

    budget = project.budget or 0

    # -----------------------------------------------------
    # Labour Cost
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
    # No material price/cost field currently exists.
    # -----------------------------------------------------

    actual_material_cost = 0.0

    # -----------------------------------------------------
    # Procurement Cost
    #
    # No procurement unit price/cost field currently exists.
    # -----------------------------------------------------

    actual_procurement_cost = 0.0

    # -----------------------------------------------------
    # Maintenance Cost
    # -----------------------------------------------------

    maintenance_records = (
        db.query(Maintenance)
        .join(
            Machinery,
            Machinery.id == Maintenance.machinery_id
        )
        .filter(
            Machinery.project_id == project_id
        )
        .all()
    )

    actual_maintenance_cost = round(
        sum(
            maintenance.cost or 0
            for maintenance in maintenance_records
        ),
        2
    )

    # -----------------------------------------------------
    # Total Actual Cost
    # -----------------------------------------------------

    total_actual_cost = round(
        actual_labour_cost
        + actual_material_cost
        + actual_procurement_cost
        + actual_maintenance_cost,
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
    # Return Budget & Cost Information
    # -----------------------------------------------------

    return {
        "project_id": project.id,
        "project_name": project.project_name,
        "budget": budget,
        "actual_labour_cost": actual_labour_cost,
        "actual_material_cost": actual_material_cost,
        "actual_procurement_cost": actual_procurement_cost,
        "actual_maintenance_cost": actual_maintenance_cost,
        "total_actual_cost": total_actual_cost,
        "remaining_budget": remaining_budget,
        "budget_utilization_percentage":
            budget_utilization_percentage
    }


# =========================================================
# GET PROJECT BY ID
# =========================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if current_user.role == "PROJECT_MANAGER" and project.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this project")

    if current_user.role == "SITE_ENGINEER":
        assigned = db.query(ProjectEngineerAssignment).filter(
            ProjectEngineerAssignment.project_id == project_id,
            ProjectEngineerAssignment.engineer_id == current_user.id,
        ).first()
        if not assigned:
            raise HTTPException(status_code=403, detail="You are not assigned to this project")

    if current_user.role not in ["ADMIN", "PROJECT_MANAGER", "SITE_ENGINEER", "CONTRACTOR", "CLIENT"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return project


# =========================================================
# UPDATE PROJECT
# =========================================================

@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
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
    # Authorization
    #
    # ADMIN can update any project.
    # MANAGER can update only assigned projects.
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can update projects"
        )

    if (
        current_user.role == "PROJECT_MANAGER"
        and project.manager_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Access Denied: "
                "You are not assigned to this project."
            )
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

    existing_project = None
    if project_data.project_code:
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

    if manager.role != "PROJECT_MANAGER":
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
        "status",
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
        "status": project_data.status,
        "manager_id": project_data.manager_id
    }

    changed_fields = []

    for field in fields_to_check:

        old_value = getattr(project, field)
        new_value = new_values[field]

        if old_value != new_value:

            changed_fields.append(field)

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

    project.project_name = project_data.project_name
    project.project_code = project_data.project_code
    project.project_category = project_data.project_category
    project.description = project_data.description
    project.location = project_data.location
    project.start_date = project_data.start_date
    project.end_date = project_data.end_date
    project.budget = project_data.budget
    project.priority = project_data.priority
    project.status = project_data.status
    project.manager_id = project_data.manager_id

    db.commit()
    db.refresh(project)

    # =====================================================
    # MODULE 8 - PROJECT UPDATE NOTIFICATION
    # =====================================================

    print(
        "MODULE 8 changed_fields:",
        changed_fields
    )

    print(
        "MODULE 8 project_id:",
        project.id
    )

    if changed_fields:

        recipients = get_project_notification_recipients(
            db=db,
            project_id=project.id
        )

        print(
            "MODULE 8 notification recipients:",
            recipients
        )

        changed_fields_text = ", ".join(
            changed_fields
        )

        for recipient in recipients:

            print(
                "MODULE 8 creating notification for:",
                recipient
            )

            create_notification(
                db=db,
                title="Project Updated",
                message=(
                    f"Project #{project.id} - "
                    f"{project.project_name} was updated. "
                    f"Changed fields: "
                    f"{changed_fields_text}."
                ),
                recipient=recipient,
                notification_type="PROJECT_UPDATE",
                project_id=project.id,
                related_entity_type="PROJECT",
                related_entity_id=project.id,
                action_url=f"/projects/project-details/{project.id}",
            )

        print(
            "MODULE 8 project update notifications created"
        )

    else:

        print(
            "MODULE 8: No project fields changed. "
            "Notification not created."
        )

    return project


# =========================================================
# UPDATE PROJECT STATUS
# =========================================================

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

    # -----------------------------------------------------
    # Authorization
    #
    # ADMIN can change any project.
    # MANAGER can change only assigned projects.
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can change project status"
        )

    if (
        current_user.role == "PROJECT_MANAGER"
        and project.manager_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Access Denied: "
                "You are not assigned to this project."
            )
        )

    current_status = project.status
    new_status = status_data.status

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

    # =====================================================
    # MODULE 8 - PROJECT STATUS NOTIFICATION
    # =====================================================

    recipients = get_project_notification_recipients(
        db=db,
        project_id=project.id
    )

    for recipient in recipients:

        create_notification(
            db=db,
            title="Project Status Updated",
            message=(
                f"Project #{project.id} - "
                f"{project.project_name} status changed "
                f"from {current_status} to {new_status}."
            ),
            recipient=recipient,
            notification_type="PROJECT_UPDATE",
            project_id=project.id,
            related_entity_type="PROJECT",
            related_entity_id=project.id,
            action_url=f"/projects/project-details/{project.id}",
        )

    return project


# =========================================================
# UPDATE PROJECT CLOSURE CONDITIONS
# =========================================================

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
    # Authorization
    #
    # ADMIN can update any project.
    # MANAGER can update only assigned projects.
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail=(
                "Only ADMIN or MANAGER can update "
                "project closure conditions"
            )
        )

    if (
        current_user.role == "PROJECT_MANAGER"
        and project.manager_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Access Denied: "
                "You are not assigned to this project."
            )
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


# =========================================================
# CLOSE PROJECT
# =========================================================

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
    # Authorization
    #
    # ADMIN can close any project.
    # MANAGER can close only assigned projects.
    # -----------------------------------------------------

    if current_user.role not in ["ADMIN", "PROJECT_MANAGER"]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or MANAGER can close projects"
        )

    if (
        current_user.role == "PROJECT_MANAGER"
        and project.manager_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Access Denied: "
                "You are not assigned to this project."
            )
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
            detail=(
                "Project cannot be closed because "
                "inspection is not approved"
            )
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


# =========================================================
# GET PROJECT HISTORY
# =========================================================

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
    # Role authorization
    # -----------------------------------------------------

    if current_user.role not in [
        "ADMIN",
        "PROJECT_MANAGER",
        "SITE_ENGINEER"
    ]:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view project history"
        )

    # -----------------------------------------------------
    # Project-level authorization
    #
    # ADMIN can view any project history.
    # MANAGER can view only assigned projects.
    # ENGINEER can view only assigned projects.
    # -----------------------------------------------------

    if (
        current_user.role == "PROJECT_MANAGER"
        and project.manager_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Access Denied: "
                "You are not assigned to this project."
            )
        )

    if current_user.role == "SITE_ENGINEER":

        engineer_assignment = (
            db.query(ProjectEngineerAssignment)
            .filter(
                ProjectEngineerAssignment.project_id == project_id,
                ProjectEngineerAssignment.engineer_id == current_user.id
            )
            .first()
        )

        if not engineer_assignment:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Access Denied: "
                    "You are not assigned to this project."
                )
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


# =========================================================
# DELETE PROJECT
# =========================================================

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
