from pydantic import BaseModel, EmailStr
<<<<<<< HEAD
from typing import Optional
=======
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str


<<<<<<< HEAD
# Used for editing an existing user. Password is intentionally optional:
# an admin editing a user's role/status shouldn't have to re-supply a
# password every time. If provided, it is re-hashed and updated.
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


=======
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
<<<<<<< HEAD
    password: str


# Self-service profile update: a logged-in user editing their own
# name/phone/email. Role and is_active are deliberately excluded here —
# those stay admin-only via UserUpdate / the /users endpoints.
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
=======
    password: str
>>>>>>> 1e31d1d67e81291f6c9db31f9ee62378fa352946
