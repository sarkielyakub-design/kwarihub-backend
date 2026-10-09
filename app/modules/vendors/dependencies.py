from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.vendors.constants import VendorStatus
from app.modules.vendors.models import Vendor
from app.modules.vendors.repository import VendorRepository


async def require_vendor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Vendor:

    role_slugs = {
        role.slug.lower()
        for role in getattr(
            current_user,
            "roles",
            [],
        )
    }

    primary_role = None

    if getattr(current_user, "role", None):
        primary_role = current_user.role.slug.lower()

    if not (
        "vendor" in role_slugs
        or primary_role == "vendor"
        or "admin" in role_slugs
        or primary_role == "admin"
        or "super-admin" in role_slugs
        or primary_role == "super-admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor access is required.",
        )

    vendor = await VendorRepository(db).get_by_user_id(
        current_user.id,
    )

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found.",
        )

    if vendor.status == VendorStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your vendor account has been suspended.",
        )

    return vendor


async def require_approved_vendor(
    vendor: Vendor = Depends(require_vendor),
) -> Vendor:

    if vendor.status != VendorStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Vendor account is {vendor.status.value}. "
                "Approval is required."
            ),
        )

    return vendor