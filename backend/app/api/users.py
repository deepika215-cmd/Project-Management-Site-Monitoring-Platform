<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
=======
from fastapi import APIRouter, Depends
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
<<<<<<< HEAD
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse

from app.core.security import hash_password
from app.core.permissions import role_required


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Only admins manage the user list. If your project needs Project
# Managers to also manage users, add "PROJECT_MANAGER" to this list.
ADMIN_ONLY = role_required(["ADMIN"])


# Create User
@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone=user.phone,
        role=user.role,
=======

router = APIRouter()

@router.post("/users")
def create_user(user: dict, db: Session = Depends(get_db)):
    new_user = User(
        name=user["name"],
        email=user["email"],
        role=user["role"],
        phone="",
        password="test123",
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

<<<<<<< HEAD

# Get All Users
@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    return db.query(User).all()


# Get User By ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Update User
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        duplicate = (
            db.query(User)
            .filter(User.email == update_data["email"], User.id != user_id)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

    if "password" in update_data:
        password = update_data.pop("password")
        if password:
            user.password = hash_password(password)
        else:
            update_data.pop("password", None)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# Delete User
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}
=======
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
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
