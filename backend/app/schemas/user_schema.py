from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal


UserRole = Literal[
    "ADMIN",
    "PROJECT_MANAGER",
    "SITE_ENGINEER",
    "CONTRACTOR",
    "WORKER",
    "CLIENT",
]


def _validate_password_strength(value: str) -> str:
    if not any(char.isupper() for char in value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(char.islower() for char in value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(char.isdigit() for char in value):
        raise ValueError("Password must contain at least one number")
    if not any(not char.isalnum() for char in value):
        raise ValueError("Password must contain at least one special character")
    return value


def _normalise_role(value: str) -> str:
    value = (value or "").strip().upper()
    legacy = {
        "MANAGER": "PROJECT_MANAGER",
        "PROJECT MANAGER": "PROJECT_MANAGER",
        "SITE ENGINEER": "SITE_ENGINEER",
        "ENGINEER": "SITE_ENGINEER",
    }
    return legacy.get(value, value)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: str = Field(..., min_length=7, max_length=20)
    role: UserRole
    employee_id: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=300)

    @field_validator("name", "phone", "employee_id", "department", "address", mode="before")
    @classmethod
    def strip_optional_strings(cls, value):
        if value is None:
            return value
        value = str(value).strip()
        return value or None

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return _normalise_role(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    employee_id: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=300)

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _normalise_role(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_password_strength(value)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    employee_id: Optional[str] = None
    department: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    employee_id: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=300)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class TestEmailRequest(BaseModel):
    email: EmailStr
