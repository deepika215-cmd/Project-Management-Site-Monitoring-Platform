from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.auth import get_current_user
from app.models.project import Project
from app.models.project_engineer_assignment import ProjectEngineerAssignment
from app.models.project_schedule import ProjectScheduleActivity
from app.models.user import User
from app.schemas.project_schedule_schema import ProjectScheduleCreate, ProjectScheduleUpdate

router = APIRouter(prefix="/project-schedules", tags=["Project Scheduling"])

ALLOWED_STATUSES = {"Not Started", "In Progress", "Completed", "Delayed"}


def _can_access_project(db: Session, project: Project, user: User) -> bool:
    role = str(user.role or "").strip().upper()
    if role == "ADMIN":
        return True
    if role in {"PROJECT_MANAGER", "MANAGER"}:
        return project.manager_id == user.id
    if role in {"SITE_ENGINEER", "ENGINEER"}:
        return db.query(ProjectEngineerAssignment).filter(
            ProjectEngineerAssignment.project_id == project.id,
            ProjectEngineerAssignment.engineer_id == user.id,
        ).first() is not None
    return False


def _project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _validate_activity(db: Session, project_id: int, data) -> None:
    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")
    if data.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid schedule status")
    dependency = (data.dependency or "").strip()
    if dependency and dependency == data.activity_name.strip():
        raise HTTPException(status_code=400, detail="An activity cannot depend on itself")
    if dependency:
        exists = db.query(ProjectScheduleActivity).filter(
            ProjectScheduleActivity.project_id == project_id,
            ProjectScheduleActivity.activity_name == dependency,
        ).first()
        if not exists:
            raise HTTPException(status_code=400, detail="Selected dependency does not exist in this project")


def _serialize(item: ProjectScheduleActivity) -> dict:
    duration = (item.end_date - item.start_date).days + 1
    return {
        "id": item.id,
        "project_id": item.project_id,
        "activity_name": item.activity_name,
        "description": item.description,
        "start_date": item.start_date,
        "end_date": item.end_date,
        "duration_days": max(duration, 0),
        "dependency": item.dependency or "",
        "status": item.status,
        "created_by": item.created_by,
    }


@router.get("/")
def get_project_schedule(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(db, project_id)
    if not _can_access_project(db, project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this project schedule")
    rows = db.query(ProjectScheduleActivity).filter(
        ProjectScheduleActivity.project_id == project_id
    ).order_by(ProjectScheduleActivity.start_date, ProjectScheduleActivity.id).all()
    return [_serialize(row) for row in rows]


@router.post("/")
def create_project_schedule_activity(
    data: ProjectScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(db, data.project_id)
    if not _can_access_project(db, project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to update this project schedule")
    if project.status == "Closed":
        raise HTTPException(status_code=400, detail="Closed projects cannot receive new schedule activities")
    _validate_activity(db, data.project_id, data)
    item = ProjectScheduleActivity(
        project_id=data.project_id,
        activity_name=data.activity_name.strip(),
        description=(data.description or "").strip() or None,
        start_date=data.start_date,
        end_date=data.end_date,
        dependency=(data.dependency or "").strip() or None,
        status=data.status,
        created_by=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.put("/{activity_id}")
def update_project_schedule_activity(
    activity_id: int,
    data: ProjectScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ProjectScheduleActivity).filter(ProjectScheduleActivity.id == activity_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Schedule activity not found")
    project = _project_or_404(db, item.project_id)
    if not _can_access_project(db, project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to update this project schedule")
    _validate_activity(db, item.project_id, data)
    item.activity_name = data.activity_name.strip()
    item.description = (data.description or "").strip() or None
    item.start_date = data.start_date
    item.end_date = data.end_date
    item.dependency = (data.dependency or "").strip() or None
    item.status = data.status
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.delete("/{activity_id}")
def delete_project_schedule_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ProjectScheduleActivity).filter(ProjectScheduleActivity.id == activity_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Schedule activity not found")
    project = _project_or_404(db, item.project_id)
    if not _can_access_project(db, project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to update this project schedule")
    # Remove references to this activity from remaining schedule rows.
    db.query(ProjectScheduleActivity).filter(
        ProjectScheduleActivity.project_id == item.project_id,
        ProjectScheduleActivity.dependency == item.activity_name,
    ).update({ProjectScheduleActivity.dependency: None}, synchronize_session=False)
    db.delete(item)
    db.commit()
    return {"message": "Schedule activity deleted successfully"}
