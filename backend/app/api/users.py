from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

router = APIRouter()

@router.post("/users")
def create_user(user: dict, db: Session = Depends(get_db)):
    new_user = User(
        name=user["name"],
        email=user["email"],
        role=user["role"],
        phone="",
        password="test123",
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.delete("/users/{email}")
def delete_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if user:
        db.delete(user)
        db.commit()
        return {"message": "User deleted"}

    return {"message": "User not found"}