from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.core.auth import get_current_user
from app.core.permissions import role_required

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -----------------------------
# Register
# -----------------------------
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

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
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -----------------------------
# Login
# -----------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -----------------------------
# Current Logged-in User
# -----------------------------
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# -----------------------------
# Admin Dashboard
# -----------------------------
@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(role_required(["ADMIN"]))
):
    return {
        "message": f"Welcome Admin {current_user.name}"
    }


# -----------------------------
# Project Manager Dashboard
# -----------------------------
@router.get("/manager")
def manager_dashboard(
    current_user: User = Depends(
        role_required(["ADMIN", "PROJECT_MANAGER"])
    )
):
    return {
        "message": f"Welcome Project Manager {current_user.name}"
    }


# -----------------------------
# Site Engineer Dashboard
# -----------------------------
@router.get("/engineer")
def engineer_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER"
        ])
    )
):
    return {
        "message": f"Welcome Site Engineer {current_user.name}"
    }


# -----------------------------
# Worker Dashboard
# -----------------------------
@router.get("/worker")
def worker_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "WORKER"
        ])
    )
):
    return {
        "message": f"Welcome Worker {current_user.name}"
    }


# -----------------------------
# Client Dashboard
# -----------------------------
@router.get("/client")
def client_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
            "WORKER",
            "CLIENT"
        ])
    )
):
    return {
        "message": f"Welcome Client {current_user.name}"
    }