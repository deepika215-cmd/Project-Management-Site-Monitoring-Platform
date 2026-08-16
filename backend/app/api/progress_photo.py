from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.progress_photo import ProgressPhoto
from app.schemas.progress_photo_schema import (
    ProgressPhotoCreate,
    ProgressPhotoResponse
)


router = APIRouter(
    prefix="/progress-photos",
    tags=["Progress Photographs"]
)


@router.post("/", response_model=ProgressPhotoResponse)
def create_progress_photo(
    photo: ProgressPhotoCreate,
    db: Session = Depends(get_db)
):
    new_photo = ProgressPhoto(**photo.model_dump())

    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    return new_photo


@router.get("/", response_model=list[ProgressPhotoResponse])
def get_progress_photos(
    db: Session = Depends(get_db)
):
    return db.query(ProgressPhoto).all()


@router.get("/{photo_id}", response_model=ProgressPhotoResponse)
def get_progress_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    photo = db.query(ProgressPhoto).filter(
        ProgressPhoto.id == photo_id
    ).first()

    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Progress Photo not found"
        )

    return photo


@router.put("/{photo_id}", response_model=ProgressPhotoResponse)
def update_progress_photo(
    photo_id: int,
    photo_data: ProgressPhotoCreate,
    db: Session = Depends(get_db)
):
    photo = db.query(ProgressPhoto).filter(
        ProgressPhoto.id == photo_id
    ).first()

    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Progress Photo not found"
        )

    for key, value in photo_data.model_dump().items():
        setattr(photo, key, value)

    db.commit()
    db.refresh(photo)

    return photo


@router.delete("/{photo_id}")
def delete_progress_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    photo = db.query(ProgressPhoto).filter(
        ProgressPhoto.id == photo_id
    ).first()

    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Progress Photo not found"
        )

    db.delete(photo)
    db.commit()

    return {
        "message": "Progress Photo deleted successfully"
    }
