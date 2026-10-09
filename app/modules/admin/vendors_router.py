from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.authorization import require_permission
from app.modules.users.models import User
from app.modules.vendors.constants import VendorStatus
from app.modules.vendors.repository import VendorRepository
from app.modules.vendors.schemas import (
    VendorRejectRequest,
    VendorResponse,
    VendorSuspendRequest,
)
from app.modules.vendors.service import VendorService


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/admin/vendors",
    tags=["Admin - Vendors"],
)


# ============================================================
# SERVICE DEPENDENCY
# ============================================================

def get_vendor_service(
    db: AsyncSession = Depends(get_db),
) -> VendorService:
    return VendorService(
        VendorRepository(db)
    )


# ============================================================
# LIST VENDORS
# ============================================================

@router.get(
    "",
    response_model=list[VendorResponse],
)
async def list_vendors(
    vendor_status: VendorStatus | None = Query(
        default=None,
        alias="status",
        description="Filter vendors by status.",
    ),
    _: User = Depends(
        require_permission("admin.vendors")
    ),
    service: VendorService = Depends(
        get_vendor_service
    ),
):
    """
    List all vendor applications.

    Optional status filter:
    - pending
    - approved
    - rejected
    - suspended
    """

    return await service.list_vendors(
        vendor_status=vendor_status
    )


# ============================================================
# GET SINGLE VENDOR
# ============================================================

@router.get(
    "/{vendor_uuid}",
    response_model=VendorResponse,
)
async def get_vendor(
    vendor_uuid: str,
    _: User = Depends(
        require_permission("admin.vendors")
    ),
    service: VendorService = Depends(
        get_vendor_service
    ),
):
    """
    Get a single vendor application by UUID.
    """

    vendor = await service.repo.get_by_uuid(
        vendor_uuid
    )

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found.",
        )

    return vendor


# ============================================================
# APPROVE VENDOR
# ============================================================

@router.patch(
    "/{vendor_uuid}/approve",
    response_model=VendorResponse,
)
async def approve_vendor(
    vendor_uuid: str,
    current_user: User = Depends(
        require_permission("admin.vendors")
    ),
    service: VendorService = Depends(
        get_vendor_service
    ),
):
    """
    Approve a pending vendor application.
    """

    return await service.approve_vendor(
        vendor_uuid=vendor_uuid,
        admin_user_id=current_user.id,
    )


# ============================================================
# REJECT VENDOR
# ============================================================

@router.patch(
    "/{vendor_uuid}/reject",
    response_model=VendorResponse,
)
async def reject_vendor(
    vendor_uuid: str,
    request: VendorRejectRequest,
    current_user: User = Depends(
        require_permission("admin.vendors")
    ),
    service: VendorService = Depends(
        get_vendor_service
    ),
):
    """
    Reject a vendor application.

    Requires:
    - rejection_reason
    - optional admin_note
    """

    return await service.reject_vendor(
        vendor_uuid=vendor_uuid,
        admin_user_id=current_user.id,
        rejection_reason=request.rejection_reason,
        admin_note=request.admin_note,
    )


# ============================================================
# SUSPEND VENDOR
# ============================================================

@router.patch(
    "/{vendor_uuid}/suspend",
    response_model=VendorResponse,
)
async def suspend_vendor(
    vendor_uuid: str,
    request: VendorSuspendRequest,
    current_user: User = Depends(
        require_permission("admin.vendors")
    ),
    service: VendorService = Depends(
        get_vendor_service
    ),
):
    """
    Suspend an approved vendor.
    """

    return await service.suspend_vendor(
        vendor_uuid=vendor_uuid,
        admin_user_id=current_user.id,
        admin_note=request.admin_note,
    )


# ============================================================
# RESTORE VENDOR
# ============================================================

@router.patch(
    "/{vendor_uuid}/restore",
    response_model=VendorResponse,
)
async def restore_vendor(
    vendor_uuid: str,
    current_user: User = Depends(
        require_permission("admin.vendors")
    ),
    service: VendorService = Depends(
        get_vendor_service
    ),
):
    """
    Restore a suspended vendor.
    """

    return await service.restore_vendor(
        vendor_uuid=vendor_uuid,
        admin_user_id=current_user.id,
    )