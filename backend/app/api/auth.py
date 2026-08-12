from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
<<<<<<< HEAD
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    ProfileUpdate,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
=======
from app.schemas.user_schema import UserCreate, UserResponse
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946

from app.core.security import (
    hash_password,
    verify_password,
<<<<<<< HEAD
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token
=======
    create_access_token
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
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
<<<<<<< HEAD
# Update My Profile
# -----------------------------
@router.put("/me", response_model=UserResponse)
def update_me(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = profile.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != current_user.email:
        duplicate = (
            db.query(User)
            .filter(User.email == update_data["email"])
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


# -----------------------------
# Change My Password
# -----------------------------
@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect"
        )

    current_user.password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# -----------------------------
# Forgot Password
# -----------------------------
# NOTE: this project has no SMTP/email service configured yet (see the
# spec's "Notifications: SMTP Email Service" item, still outstanding).
# Until that's wired up, the reset link is printed to the backend
# console instead of emailed, so this is fully testable locally. Swap
# the print() below for a real email send once SMTP settings exist.
@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()

    # Always return the same generic message whether or not the email
    # exists, so this endpoint can't be used to enumerate registered users.
    generic_response = {
        "message": "If an account with that email exists, a password reset link has been sent."
    }

    if not user:
        return generic_response

    reset_token = create_password_reset_token(user.email)

    print(
        "\n[PASSWORD RESET] "
        f"Reset link for {user.email}: "
        f"http://localhost:4200/reset-password?token={reset_token}\n"
    )

    return generic_response


# -----------------------------
# Reset Password
# -----------------------------
@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    email = verify_password_reset_token(payload.token)

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link. Please request a new one."
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password reset successfully. You can now log in."}


# -----------------------------
=======
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
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