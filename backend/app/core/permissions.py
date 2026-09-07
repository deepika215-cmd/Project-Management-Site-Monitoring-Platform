from typing import Iterable, List

from fastapi import Depends, HTTPException

from app.core.auth import get_current_user
from app.models.user import User


ROLE_ALIASES = {
    "MANAGER": "PROJECT_MANAGER",
    "PROJECT MANAGER": "PROJECT_MANAGER",
    "PM": "PROJECT_MANAGER",
    "ENGINEER": "SITE_ENGINEER",
    "SITE ENGINEER": "SITE_ENGINEER",
}


def normalize_role(role: str | None) -> str:
    """Return the canonical role used by the Angular application/API."""
    value = str(role or "").strip().upper().replace("-", "_")
    value = "_".join(value.split())
    return ROLE_ALIASES.get(value, value)


def has_role(user: User, allowed_roles: Iterable[str]) -> bool:
    current = normalize_role(getattr(user, "role", None))
    allowed = {normalize_role(role) for role in allowed_roles}
    return current in allowed


def role_required(allowed_roles: List[str]):
    """FastAPI dependency for role-based access control.

    Legacy database values MANAGER/ENGINEER are accepted and normalized to
    PROJECT_MANAGER/SITE_ENGINEER so older databases continue to work.
    """
    def checker(current_user: User = Depends(get_current_user)):
        if not has_role(current_user, allowed_roles):
            raise HTTPException(
                status_code=403,
                detail="Access Denied: You don't have permission.",
            )
        return current_user

    return checker
