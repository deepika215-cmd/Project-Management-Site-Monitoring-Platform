from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    ProfileUpdate,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from app.core.auth import get_current_user
from app.core.permissions import role_required

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone=user.phone,
        role=user.role,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password",
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    if not verify_password(
        form_data.password,
        db_user.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password",
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone,
            "role": db_user.role,
            "is_active": db_user.is_active,
        },
    }


# ============================================================
# CURRENT LOGGED-IN USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ============================================================
# UPDATE MY PROFILE
# ============================================================

@router.put(
    "/me",
    response_model=UserResponse,
)
def update_me(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = profile.model_dump(
        exclude_unset=True
    )

    # Check whether the new email already belongs to
    # another user.
    if (
        "email" in update_data
        and update_data["email"] != current_user.email
    ):
        duplicate = (
            db.query(User)
            .filter(
                User.email == update_data["email"],
                User.id != current_user.id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Email already exists",
            )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return current_user


# ============================================================
# CHANGE MY PASSWORD
# ============================================================

@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(
        payload.current_password,
        current_user.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect",
        )

    current_user.password = hash_password(
        payload.new_password
    )

    db.commit()

    return {
        "message": "Password updated successfully"
    }


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    # Always return the same response whether or not the
    # email exists. This prevents user enumeration.
    generic_response = {
        "message": (
            "If an account with that email exists, "
            "a password reset link has been sent."
        )
    }

    if not user:
        return generic_response

    reset_token = create_password_reset_token(
        user.email
    )

    # SMTP/email service is not configured yet.
    # Print the reset link for local development.
    print(
        "\n[PASSWORD RESET] "
        f"Reset link for {user.email}: "
        f"http://localhost:4200/reset-password"
        f"?token={reset_token}\n"
    )

    return generic_response


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    email = verify_password_reset_token(
        payload.token
    )

    if not email:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid or expired reset link. "
                "Please request a new one."
            ),
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.password = hash_password(
        payload.new_password
    )

    db.commit()

    return {
        "message": (
            "Password reset successfully. "
            "You can now log in."
        )
    }


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(
        role_required(["ADMIN"])
    ),
):
    return {
        "message": f"Welcome Admin {current_user.name}"
    }


# ============================================================
# PROJECT MANAGER DASHBOARD
# ============================================================

@router.get("/manager")
def manager_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
        ])
    ),
):
    return {
        "message": (
            f"Welcome Project Manager "
            f"{current_user.name}"
        )
    }


# ============================================================
# SITE ENGINEER DASHBOARD
# ============================================================

@router.get("/engineer")
def engineer_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
        ])
    ),
):
    return {
        "message": (
            f"Welcome Site Engineer "
            f"{current_user.name}"
        )
    }


# ============================================================
# WORKER DASHBOARD
# ============================================================

@router.get("/worker")
def worker_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "WORKER",
        ])
    ),
):
    return {
        "message": (
            f"Welcome Worker "
            f"{current_user.name}"
        )
    }


# ============================================================
# CLIENT DASHBOARD
# ============================================================

@router.get("/client")
def client_dashboard(
    current_user: User = Depends(
        role_required([
            "ADMIN",
            "MANAGER",
            "ENGINEER",
            "WORKER",
            "CLIENT",
        ])
    ),
):
    return {
        "message": (
            f"Welcome Client "
            f"{current_user.name}"
        )
    }