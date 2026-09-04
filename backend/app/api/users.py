from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse

from app.core.security import hash_password
from app.core.permissions import role_required


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Only admins manage the user list.
ADMIN_ONLY = role_required(["ADMIN"])


# ============================================================
# Create User
# ============================================================

@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

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
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# Get All Users
# ============================================================

@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    return db.query(User).all()


# ============================================================
# Get User By ID
# ============================================================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ============================================================
# Update User
# ============================================================

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    update_data = user_data.model_dump(exclude_unset=True)

    # --------------------------------------------------------
    # Prevent duplicate email addresses
    # --------------------------------------------------------

    if "email" in update_data:
        duplicate = (
            db.query(User)
            .filter(
                User.email == update_data["email"],
                User.id != user_id
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

    # --------------------------------------------------------
    # Handle password separately
    # --------------------------------------------------------

    if "password" in update_data:
        password = update_data.pop("password")

        if password:
            user.password = hash_password(password)

    # --------------------------------------------------------
    # Update remaining fields
    # --------------------------------------------------------

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# ============================================================
# Delete User
# ============================================================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(ADMIN_ONLY)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted"
    }