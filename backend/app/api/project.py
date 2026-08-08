from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.project import Project
from app.models.project_milestone import ProjectMilestone

from app.schemas.project_schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatusUpdate
)

from app.schemas.project_tracking import ProjectTrackingResponse


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
    db: Session = Depends(get_db)
):

    # Validate project dates
    if project.end_date < project.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # Validate budget
    if project.budget < 0:
        raise HTTPException(
            status_code=400,
            detail="Budget cannot be negative"
        )

    new_project = Project(
        **project.model_dump()
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

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

    # Find project
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Get all milestones belonging to this project
    milestones = db.query(ProjectMilestone).filter(
        ProjectMilestone.project_id == project_id
    ).all()

    # Total milestones
    total_milestones = len(milestones)

    # Completed milestones
    completed_milestones = len([
        milestone
        for milestone in milestones
        if milestone.status == "Completed"
    ])

    # Pending milestones
    pending_milestones = (
        total_milestones - completed_milestones
    )

    # Calculate project progress
    progress = 0

    if total_milestones > 0:
        progress = round(
            (completed_milestones / total_milestones) * 100,
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

    # Do not modify closed projects
    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # Validate dates
    if project_data.end_date < project_data.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # Validate budget
    if project_data.budget < 0:
        raise HTTPException(
            status_code=400,
            detail="Budget cannot be negative"
        )

    for key, value in project_data.model_dump().items():
        setattr(project, key, value)

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

    current_status = project.status
    new_status = status_data.status

    # Prevent changing a closed project
    if current_status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Closed project cannot be modified"
        )

    # Validate status flow
    allowed_transitions = {
        "Planning": ["In Progress"],
        "In Progress": ["Completed"],
        "Completed": ["Closed"],
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

    project.status = new_status

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

    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Project is already closed"
        )

    if project.status != "Completed":
        raise HTTPException(
            status_code=400,
            detail="Only completed projects can be closed"
        )

    project.status = "Closed"

    db.commit()
    db.refresh(project)

    return project


# ---------------------------------------------------------
# Delete Project
# ---------------------------------------------------------

@router.delete("/{project_id}")
def delete_project(
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

    # Do not delete closed projects
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