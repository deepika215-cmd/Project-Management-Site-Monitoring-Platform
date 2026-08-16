from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.project import Project
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectResponse
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# GET ALL PROJECTS
@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(
    db: Session = Depends(get_db)
):
    return db.query(Project).all()


# GET PROJECT BY ID
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


# CREATE PROJECT
@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    new_project = Project(
        **project.model_dump()
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# UPDATE PROJECT
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    updated_project: ProjectCreate,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    for key, value in updated_project.model_dump().items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


# DELETE PROJECT
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }