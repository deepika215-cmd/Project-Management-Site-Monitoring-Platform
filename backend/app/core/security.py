from datetime import datetime, timedelta
<<<<<<< HEAD
from jose import jwt, JWTError
=======
from jose import jwt
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
from passlib.context import CryptContext

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

<<<<<<< HEAD
# Password reset tokens are short-lived and carry a "purpose" claim so
# they can never be replayed as a normal login/access token.
PASSWORD_RESET_EXPIRE_MINUTES = 15
PASSWORD_RESET_PURPOSE = "password_reset"

=======
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946

def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
<<<<<<< HEAD
    )


def create_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=PASSWORD_RESET_EXPIRE_MINUTES
    )

    return jwt.encode(
        {
            "sub": email,
            "purpose": PASSWORD_RESET_PURPOSE,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_password_reset_token(token: str) -> str | None:
    """Returns the email the token was issued for, or None if the
    token is invalid, expired, or not a password-reset token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

    if payload.get("purpose") != PASSWORD_RESET_PURPOSE:
        return None

    return payload.get("sub")
=======
    )
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
