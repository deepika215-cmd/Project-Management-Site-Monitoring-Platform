from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.daily_progress import DailyProgress
from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.user import User

from app.core.permissions import role_required

from app.schemas.daily_progress_schema import (
    DailyProgressCreate,
    DailyProgressResponse,
)


router = APIRouter(
    prefix="/daily-progress",
    tags=["Daily Progress"],
)


# =========================================================
# CREATE DAILY PROGRESS
# ADMIN / MANAGER / ENGINEER
# =========================================================
@router.post(
    "/",
    response_model=DailyProgressResponse
)
def create_daily_progress(
    progress: DailyProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER", "ENGINEER"])
    ),
):

    # -----------------------------------------------------
    # Validate project
    # -----------------------------------------------------
    project = db.query(Project).filter(
        Project.id == progress.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Do not allow progress on closed project
    # -----------------------------------------------------
    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot add progress to a closed project"
        )

    # -----------------------------------------------------
    # Validate milestone
    # -----------------------------------------------------
    milestone = None

    if progress.milestone_id is not None:

        milestone = db.query(ProjectMilestone).filter(
            ProjectMilestone.id == progress.milestone_id
        ).first()

        if milestone is None:
            raise HTTPException(
                status_code=404,
                detail="Milestone not found"
            )

        if milestone.project_id != progress.project_id:
            raise HTTPException(
                status_code=400,
                detail="Milestone does not belong to this project"
            )

    # -----------------------------------------------------
    # Validate completion percentage
    # -----------------------------------------------------
    if not 0 <= progress.completion_percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Completion percentage must be between 0 and 100"
        )

    # -----------------------------------------------------
    # Create daily progress record
    # -----------------------------------------------------
    new_progress = DailyProgress(
        **progress.model_dump()
    )

    db.add(new_progress)

    # -----------------------------------------------------
    # AUTOMATIC MILESTONE COMPLETION
    #
    # Milestone becomes Completed only when:
    #
    # 1. A milestone is linked
    # 2. Progress reaches 100%
    # 3. Quality verification is true
    # -----------------------------------------------------
    if (
        milestone is not None
        and progress.completion_percentage >= 100
        and progress.quality_verified
    ):
        milestone.status = "Completed"

    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------
    db.commit()

    db.refresh(new_progress)

    return new_progress


# =========================================================
# GET ALL DAILY PROGRESS
# ADMIN / MANAGER / ENGINEER / CLIENT
# =========================================================
@router.get(
    "/",
    response_model=list[DailyProgressResponse]
)
def get_all_daily_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(
            ["ADMIN", "MANAGER", "ENGINEER", "CLIENT"]
        )
    ),
):

    return db.query(DailyProgress).all()


# =========================================================
# GET DAILY PROGRESS BY ID
# ADMIN / MANAGER / ENGINEER / CLIENT
# =========================================================
@router.get(
    "/{progress_id}",
    response_model=DailyProgressResponse
)
def get_daily_progress_by_id(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(
            ["ADMIN", "MANAGER", "ENGINEER", "CLIENT"]
        )
    ),
):

    progress = db.query(DailyProgress).filter(
        DailyProgress.id == progress_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    return progress


# =========================================================
# UPDATE DAILY PROGRESS
# ADMIN / MANAGER / ENGINEER
# =========================================================
@router.put(
    "/{progress_id}",
    response_model=DailyProgressResponse
)
def update_daily_progress(
    progress_id: int,
    updated_progress: DailyProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(
            ["ADMIN", "MANAGER", "ENGINEER"]
        )
    ),
):

    # -----------------------------------------------------
    # Find existing progress
    # -----------------------------------------------------
    progress = db.query(DailyProgress).filter(
        DailyProgress.id == progress_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    # -----------------------------------------------------
    # Validate project
    # -----------------------------------------------------
    project = db.query(Project).filter(
        Project.id == updated_progress.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # -----------------------------------------------------
    # Do not allow updates on closed project
    # -----------------------------------------------------
    if project.status == "Closed":
        raise HTTPException(
            status_code=400,
            detail="Cannot update progress for a closed project"
        )

    # -----------------------------------------------------
    # Validate milestone
    # -----------------------------------------------------
    milestone = None

    if updated_progress.milestone_id is not None:

        milestone = db.query(ProjectMilestone).filter(
            ProjectMilestone.id ==
            updated_progress.milestone_id
        ).first()

        if milestone is None:
            raise HTTPException(
                status_code=404,
                detail="Milestone not found"
            )

        if milestone.project_id != updated_progress.project_id:
            raise HTTPException(
                status_code=400,
                detail="Milestone does not belong to this project"
            )

    # -----------------------------------------------------
    # Validate completion percentage
    # -----------------------------------------------------
    if not 0 <= updated_progress.completion_percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Completion percentage must be between 0 and 100"
        )

    # -----------------------------------------------------
    # Update progress fields
    # -----------------------------------------------------
    for key, value in updated_progress.model_dump().items():
        setattr(progress, key, value)

    # -----------------------------------------------------
    # AUTOMATIC MILESTONE COMPLETION
    #
    # If updated progress reaches 100% and is verified,
    # automatically complete the milestone.
    # -----------------------------------------------------
    if (
        milestone is not None
        and updated_progress.completion_percentage >= 100
        and updated_progress.quality_verified
    ):
        milestone.status = "Completed"

    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------
    db.commit()

    db.refresh(progress)

    return progress


# =========================================================
# DELETE DAILY PROGRESS
# ADMIN / MANAGER ONLY
# =========================================================
@router.delete(
    "/{progress_id}"
)
def delete_daily_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required(["ADMIN", "MANAGER"])
    ),
):

    # -----------------------------------------------------
    # Find progress
    # -----------------------------------------------------
    progress = db.query(DailyProgress).filter(
        DailyProgress.id == progress_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Daily Progress not found"
        )

    # -----------------------------------------------------
    # Delete progress
    # -----------------------------------------------------
    db.delete(progress)

    db.commit()

    return {
        "message": "Daily Progress deleted successfully"
    }