from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.auth import get_current_user

from app.models.project import Project
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.user import User

from app.schemas.project_engineer_assignment import (
    ProjectEngineerAssignmentCreate,
    ProjectEngineerAssignmentResponse
)

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/projects",
    tags=["Project Engineer Assignments"]
)


# ============================================================
# Assign Site Engineer to Project
# ============================================================

@router.post(
    "/{project_id}/engineers",
    response_model=ProjectEngineerAssignmentResponse
)
def assign_engineer(
    project_id: int,
    assignment_data: ProjectEngineerAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Closed projects cannot be modified
    # --------------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # --------------------------------------------------------
    # Check permission
    #
    # ADMIN can assign engineers to any project.
    # MANAGER can assign engineers only to their own project.
    # --------------------------------------------------------

    if current_user.role == "ADMIN":
        pass

    elif (
        current_user.role == "MANAGER"
        and current_user.id == project.manager_id
    ):
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or the Project Manager can assign Site Engineers"
        )

    # --------------------------------------------------------
    # Check engineer
    # --------------------------------------------------------

    engineer = db.query(User).filter(
        User.id == assignment_data.engineer_id
    ).first()

    if not engineer:
        raise HTTPException(
            status_code=404,
            detail="Engineer not found"
        )

    # --------------------------------------------------------
    # User must have ENGINEER role
    # --------------------------------------------------------

    if engineer.role != "ENGINEER":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not an ENGINEER"
        )

    # --------------------------------------------------------
    # Engineer must be active
    # --------------------------------------------------------

    if not engineer.is_active:
        raise HTTPException(
            status_code=400,
            detail="Selected engineer is inactive"
        )

    # --------------------------------------------------------
    # Check duplicate assignment
    # --------------------------------------------------------

    existing_assignment = db.query(
        ProjectEngineerAssignment
    ).filter(
        ProjectEngineerAssignment.project_id == project_id,
        ProjectEngineerAssignment.engineer_id ==
        assignment_data.engineer_id
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="Engineer is already assigned to this project"
        )

    # --------------------------------------------------------
    # Create assignment
    # --------------------------------------------------------

    new_assignment = ProjectEngineerAssignment(
        project_id=project_id,
        engineer_id=assignment_data.engineer_id
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    # --------------------------------------------------------
    # Module 8 - Notify the assigned engineer
    # --------------------------------------------------------

    create_notification(
        db=db,
        title="Engineer Assigned to Project",
        message=(
            f"You have been assigned as a Site Engineer to "
            f"Project #{project.id} - {project.project_name}."
        ),
        recipient=engineer.email
    )

    return new_assignment


# ============================================================
# Get Engineers Assigned to Project
# ============================================================

@router.get(
    "/{project_id}/engineers",
    response_model=list[ProjectEngineerAssignmentResponse]
)
def get_project_engineers(
    project_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Get assignments
    # --------------------------------------------------------

    assignments = db.query(
        ProjectEngineerAssignment
    ).filter(
        ProjectEngineerAssignment.project_id == project_id
    ).all()

    return assignments


# ============================================================
# Remove Site Engineer from Project
# ============================================================

@router.delete(
    "/{project_id}/engineers/{engineer_id}"
)
def remove_engineer(
    project_id: int,
    engineer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # --------------------------------------------------------
    # Check permission
    #
    # ADMIN can remove engineers from any project.
    # MANAGER can remove engineers only from their own project.
    # --------------------------------------------------------

    if current_user.role == "ADMIN":
        pass

    elif (
        current_user.role == "MANAGER"
        and current_user.id == project.manager_id
    ):
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN or the Project Manager can remove Site Engineers"
        )

    # --------------------------------------------------------
    # Closed projects cannot be modified
    # --------------------------------------------------------

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # --------------------------------------------------------
    # Find assignment
    # --------------------------------------------------------

    assignment = db.query(
        ProjectEngineerAssignment
    ).filter(
        ProjectEngineerAssignment.project_id == project_id,
        ProjectEngineerAssignment.engineer_id == engineer_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Engineer is not assigned to this project"
        )

    # --------------------------------------------------------
    # Remove assignment
    # --------------------------------------------------------

    db.delete(assignment)
    db.commit()

    return {
        "message": "Site Engineer removed from project successfully"
    }