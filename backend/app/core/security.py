from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# Password hashing
# ============================================================

def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its hashed value."""
    return pwd_context.verify(password, hashed_password)


# ============================================================
# Access token
# ============================================================

def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# Password reset token
# ============================================================

PASSWORD_RESET_EXPIRE_MINUTES = 15
PASSWORD_RESET_PURPOSE = "password_reset"


def create_password_reset_token(email: str) -> str:
    """Create a short-lived password reset token."""
    expire = datetime.utcnow() + timedelta(
        minutes=PASSWORD_RESET_EXPIRE_MINUTES
    )

    return jwt.encode(
        {
            "sub": email,
            "purpose": PASSWORD_RESET_PURPOSE,
            "exp": expire,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify a password reset token.

    Returns:
        The email associated with the token if valid.
        None if the token is invalid, expired, or not a
        password-reset token.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        return None

    if payload.get("purpose") != PASSWORD_RESET_PURPOSE:
        return None

    return payload.get("sub")