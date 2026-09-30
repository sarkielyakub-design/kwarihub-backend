from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.modules.auth.dependencies import (
    get_current_user,
)
from app.modules.roles.models import Role
from app.modules.users.models import User


# ============================================================
# LOAD USER WITH ALL ROLES
# ============================================================

async def get_authorized_user(
    current_user: User = Depends(
        get_current_user,
    ),
    db=Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles)
            .selectinload(Role.permissions)
        )
        .where(
            User.id == current_user.id,
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deleted.",
        )

    return user


# ============================================================
# ROLE CHECK
# ============================================================

def require_role(
    *allowed_roles: str,
) -> Callable:

    allowed = {
        value.lower().strip()
        for value in allowed_roles
    }

    async def dependency(
        user: User = Depends(
            get_authorized_user,
        ),
    ):
        user_roles = {
            role.slug.lower()
            for role in user.roles
        }

        # Super Admin bypasses all role checks.
        if "super-admin" in user_roles:
            return user

        if not user_roles.intersection(
            allowed
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource."
                ),
            )

        return user

    return dependency


# ============================================================
# PERMISSION CHECK
# ============================================================

def require_permission(
    permission_name: str,
) -> Callable:

    required = permission_name.lower().strip()

    async def dependency(
        user: User = Depends(
            get_authorized_user,
        ),
    ):
        role_slugs = {
            role.slug.lower()
            for role in user.roles
        }

        # Super Admin has everything.
        if "super-admin" in role_slugs:
            return user

        permissions = {
            permission.name.lower()
            for role in user.roles
            for permission in role.permissions
        }

        if required not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Missing permission: "
                    f"{permission_name}"
                ),
            )

        return user

    return dependency