from fastapi import APIRouter, Depends, HTTPException
from time import time
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.config import (
    FRONTEND_BASE_URL,
    BUILDTRACK_EXPOSE_RESET_LINK,
)
from app.models.user import User

from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserResponse,
    ProfileUpdate,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TestEmailRequest,
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

from app.services.email_service import (
    is_smtp_configured,
    send_password_reset_email,
    send_test_email,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)



def _user_payload(user: User) -> dict:
    """Return one consistent user object for auth/login/profile responses."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
        "employee_id": getattr(user, "employee_id", None),
        "department": getattr(user, "department", None),
        "address": getattr(user, "address", None),
    }


def _normalised_email(email: str) -> str:
    return str(email or "").strip().lower()


def _should_expose_reset_link() -> bool:
    """Expose reset links only when explicitly allowed for local testing."""
    # When real SMTP is configured, do not show reset tokens on screen unless
    # the developer intentionally keeps BUILDTRACK_EXPOSE_RESET_LINK=true.
    return bool(BUILDTRACK_EXPOSE_RESET_LINK)


def _password_reset_link(reset_token: str) -> str:
    base_url = str(FRONTEND_BASE_URL or "http://localhost:4200").rstrip("/")
    return f"{base_url}/reset-password?token={reset_token}"

# ============================================================
# BASIC LOGIN RATE LIMITING
# ============================================================

LOGIN_RATE_LIMIT_WINDOW_SECONDS = 300
LOGIN_RATE_LIMIT_MAX_FAILURES = 5
_login_failures: dict[str, list[float]] = {}


def _check_login_rate_limit(email: str) -> None:
    """Block repeated failed login attempts for a short time window.

    This is an in-memory development/demo safeguard. In production, move this
    to Redis or another shared store if multiple backend instances are used.
    """
    now = time()
    attempts = [
        attempt
        for attempt in _login_failures.get(email, [])
        if now - attempt < LOGIN_RATE_LIMIT_WINDOW_SECONDS
    ]
    _login_failures[email] = attempts

    if len(attempts) >= LOGIN_RATE_LIMIT_MAX_FAILURES:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again after 5 minutes.",
        )


def _record_failed_login(email: str) -> None:
    now = time()
    attempts = [
        attempt
        for attempt in _login_failures.get(email, [])
        if now - attempt < LOGIN_RATE_LIMIT_WINDOW_SECONDS
    ]
    attempts.append(now)
    _login_failures[email] = attempts


def _clear_failed_logins(email: str) -> None:
    _login_failures.pop(email, None)



# ============================================================
# REGISTER
# ============================================================

@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    email = _normalised_email(user.email)
    role = str(user.role).strip().upper()

    # Prevent users from creating an ADMIN account
    # through public registration.
    if role == "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Public registration as ADMIN is not allowed",
        )

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    new_user = User(
        name=user.name.strip(),
        email=email,
        password=hash_password(user.password),
        phone=user.phone.strip(),
        role=role,
        employee_id=user.employee_id,
        department=user.department,
        address=user.address,
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
    email = _normalised_email(form_data.username)
    _check_login_rate_limit(email)

    db_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not db_user:
        _record_failed_login(email)
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
        _record_failed_login(email)
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password",
        )

    _clear_failed_logins(email)

    token = create_access_token(
        {
            "sub": db_user.email,
            "role": db_user.role,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _user_payload(db_user),
    }


# ============================================================
# JSON LOGIN (used by the Angular frontend)
# ============================================================

@router.post("/login-json")
def login_json(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """Login with a normal JSON payload.

    The OAuth2 form endpoint above is kept for Swagger/OAuth2 compatibility,
    while Angular uses this endpoint to avoid form-encoding/browser issues.
    """
    email = _normalised_email(credentials.email)
    _check_login_rate_limit(email)

    db_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not db_user or not verify_password(credentials.password, db_user.password):
        _record_failed_login(email)
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    _clear_failed_logins(email)

    token = create_access_token({"sub": db_user.email, "role": db_user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _user_payload(db_user),
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
    if "email" in update_data and update_data["email"]:
        update_data["email"] = _normalised_email(update_data["email"])

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
        .filter(User.email == _normalised_email(payload.email))
        .first()
    )

    # Always use a generic message so unregistered emails cannot be detected
    # from the frontend response.
    generic_response = {
        "message": (
            "If an account with that email exists, "
            "a password reset link has been sent."
        )
    }

    if not user:
        return generic_response

    reset_token = create_password_reset_token(user.email)
    reset_link = _password_reset_link(reset_token)

    email_sent = False
    email_error = None

    try:
        email_sent = send_password_reset_email(user.email, reset_link)
    except Exception as exc:
        email_error = str(exc)
        print(
            "\n[PASSWORD RESET EMAIL ERROR] "
            f"Could not send reset email to {user.email}: {email_error}\n"
        )

    if email_sent:
        return generic_response

    print(
        "\n[PASSWORD RESET DEV LINK] "
        f"Reset link for {user.email}: {reset_link}\n"
    )

    # For local testing, return the link only when enabled.
    # In real use, set BUILDTRACK_EXPOSE_RESET_LINK=false.
    if _should_expose_reset_link():
        reason = "SMTP is not configured"
        if is_smtp_configured() and email_error:
            reason = f"SMTP sending failed: {email_error}"
        elif is_smtp_configured():
            reason = "SMTP sending returned false"

        return {
            **generic_response,
            "reset_link": reset_link,
            "reset_token": reset_token,
            "email_sent": False,
            "smtp_configured": is_smtp_configured(),
            "development_note": (
                f"{reason}. The reset link is shown only because "
                "BUILDTRACK_EXPOSE_RESET_LINK is enabled for local testing."
            ),
        }

    # Production-safe response. Error details are logged only in the terminal.
    return generic_response


# ============================================================
# ADMIN SMTP TEST
# ============================================================

@router.post("/test-email")
def test_email(
    payload: TestEmailRequest,
    current_user: User = Depends(role_required(["ADMIN"])),
):
    """Send a test email to verify SMTP settings. Admin only."""
    if not is_smtp_configured():
        raise HTTPException(
            status_code=400,
            detail="SMTP is not configured. Update backend/.env first.",
        )

    try:
        send_test_email(str(payload.email))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"SMTP test failed: {exc}",
        )

    return {"message": "Test email sent successfully"}


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
            "PROJECT_MANAGER",
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
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
            "PROJECT_MANAGER",
            "SITE_ENGINEER",
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