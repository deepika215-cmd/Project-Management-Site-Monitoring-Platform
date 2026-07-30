from typing import List

from fastapi import Depends, HTTPException

from app.core.auth import get_current_user
from app.models.user import User


def role_required(allowed_roles: List[str]):

    def checker(
        current_user: User = Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access Denied: You don't have permission."
            )

        return current_user

    return checker
    