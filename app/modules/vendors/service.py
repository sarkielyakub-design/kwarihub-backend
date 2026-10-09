from decimal import Decimal
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.orders.models import OrderStatus
from app.modules.roles.models import Role
from app.modules.roles.association import user_roles
from app.modules.vendors.constants import VendorStatus
from app.modules.vendors.models import Vendor
from app.modules.vendors.repository import VendorRepository
from app.modules.vendors.schemas import (
    VendorApplicationRequest,
    VendorDashboardResponse,
    VendorOrderItemResponse,
    VendorUpdateRequest,
)


class VendorService:

    def __init__(
        self,
        repo: VendorRepository,
    ):
        self.repo = repo
        self.db: AsyncSession = repo.db

    # ============================================================
    # APPLICATION
    # ============================================================

    async def create_application(
        self,
        user,
        request: VendorApplicationRequest,
    ):
        existing = await self.repo.get_by_user_id(user.id)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendor application already exists.",
            )

        # --------------------------------------------------------
        # Find Vendor role
        # --------------------------------------------------------

        result = await self.db.execute(
            select(Role).where(
                Role.slug == "vendor",
                Role.is_deleted.is_(False),
                Role.is_active.is_(True),
            )
        )

        vendor_role = result.scalar_one_or_none()

        if not vendor_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Vendor role is not configured.",
            )

        # --------------------------------------------------------
        # Add vendor role to user if not already assigned
        # --------------------------------------------------------

        role_exists = await self.db.scalar(
            select(user_roles.c.user_id).where(
                user_roles.c.user_id == user.id,
                user_roles.c.role_id == vendor_role.id,
            )
        )

        if role_exists is None:
            await self.db.execute(
                user_roles.insert().values(
                    user_id=user.id,
                    role_id=vendor_role.id,
                )
            )

        # --------------------------------------------------------
        # Create vendor application
        # --------------------------------------------------------

        vendor = Vendor(
            user_id=user.id,
            business_name=request.business_name.strip(),
            business_description=(
                request.business_description.strip()
                if request.business_description
                else None
            ),
            business_phone=request.business_phone.strip(),
            business_email=str(request.business_email).lower().strip(),
            country=request.country.strip(),
            state=request.state.strip(),
            city=request.city.strip(),
            address=request.address.strip(),
            status=VendorStatus.PENDING,
        )

        self.db.add(vendor)

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # GET APPLICATION
    # ============================================================

    async def get_application(
        self,
        user_id: int,
    ):
        vendor = await self.repo.get_by_user_id(user_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor application not found.",
            )

        return vendor

    # ============================================================
    # UPDATE APPLICATION
    # ============================================================

    async def update_application(
        self,
        user_id: int,
        request: VendorUpdateRequest,
    ):
        vendor = await self.repo.get_by_user_id(user_id)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor application not found.",
            )

        if vendor.status == VendorStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Suspended vendors cannot update their profile.",
            )

        data = request.model_dump(
            exclude_unset=True,
        )

        for key, value in data.items():
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()

                setattr(vendor, key, value)

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # ADMIN APPROVAL
    # ============================================================

    async def approve_vendor(
        self,
        vendor_uuid: str,
        admin_user_id: int,
    ):
        vendor = await self.repo.get_by_uuid(vendor_uuid)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        if vendor.status == VendorStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vendor is already approved.",
            )

        if vendor.status == VendorStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Suspended vendor cannot be approved directly.",
            )

        now = datetime.now(timezone.utc)

        vendor.status = VendorStatus.APPROVED
        vendor.rejection_reason = None
        vendor.reviewed_by = admin_user_id
        vendor.reviewed_at = now
        vendor.approved_at = now
        vendor.rejected_at = None
        vendor.suspended_at = None

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # ADMIN REJECTION
    # ============================================================

    async def reject_vendor(
        self,
        vendor_uuid: str,
        admin_user_id: int,
        rejection_reason: str,
        admin_note: str | None = None,
    ):
        vendor = await self.repo.get_by_uuid(vendor_uuid)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        if vendor.status == VendorStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An approved vendor cannot be rejected.",
            )

        if not rejection_reason.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Rejection reason is required.",
            )

        now = datetime.now(timezone.utc)

        vendor.status = VendorStatus.REJECTED
        vendor.rejection_reason = rejection_reason.strip()
        vendor.admin_note = (
            admin_note.strip()
            if admin_note
            else None
        )
        vendor.reviewed_by = admin_user_id
        vendor.reviewed_at = now
        vendor.rejected_at = now
        vendor.approved_at = None
        vendor.suspended_at = None

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # ADMIN SUSPENSION
    # ============================================================

    async def suspend_vendor(
        self,
        vendor_uuid: str,
        admin_user_id: int,
        admin_note: str | None = None,
    ):
        vendor = await self.repo.get_by_uuid(vendor_uuid)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        if vendor.status != VendorStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only approved vendors can be suspended.",
            )

        now = datetime.now(timezone.utc)

        vendor.status = VendorStatus.SUSPENDED
        vendor.admin_note = (
            admin_note.strip()
            if admin_note
            else None
        )
        vendor.reviewed_by = admin_user_id
        vendor.reviewed_at = now
        vendor.suspended_at = now

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # ADMIN RESTORE
    # ============================================================

    async def restore_vendor(
        self,
        vendor_uuid: str,
        admin_user_id: int,
    ):
        vendor = await self.repo.get_by_uuid(vendor_uuid)

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        if vendor.status != VendorStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only suspended vendors can be restored.",
            )

        now = datetime.now(timezone.utc)

        vendor.status = VendorStatus.APPROVED
        vendor.reviewed_by = admin_user_id
        vendor.reviewed_at = now
        vendor.suspended_at = None

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # ORDERS
    # ============================================================

    @staticmethod
    def order_item_to_response(
        item,
    ) -> VendorOrderItemResponse:

        return VendorOrderItemResponse(
            uuid=str(item.uuid),
            order_uuid=str(item.order.uuid),
            order_number=item.order.order_number,
            product_id=item.product_id,
            product_name=item.product_name,
            variant_name=item.variant_name,
            quantity=item.quantity,
            unit_price=Decimal(str(item.unit_price)),
            total_price=Decimal(str(item.total_price)),
            order_status=item.order.status.value,
            shipping_address=item.order.shipping_address,
            created_at=item.order.created_at,
        )

    async def orders(
        self,
        seller_id: int,
    ):
        items = await self.repo.get_vendor_orders(
            seller_id,
        )

        return [
            self.order_item_to_response(item)
            for item in items
        ]

    async def get_order(
        self,
        seller_id: int,
        item_uuid: str,
    ):
        item = await self.repo.get_vendor_order_item(
            seller_id,
            item_uuid,
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor order item not found.",
            )

        return self.order_item_to_response(item)

    # ============================================================
    # DASHBOARD
    # ============================================================

    async def dashboard(
        self,
        vendor: Vendor,
    ):

        seller_id = vendor.user_id

        total_products = await self.repo.count_products(
            seller_id,
        )

        active_products = await self.repo.count_active_products(
            seller_id,
        )

        total_orders = await self.repo.count_orders(
            seller_id,
        )

        pending_orders = await self.repo.count_orders_by_status(
            seller_id,
            OrderStatus.PENDING,
        )

        processing_orders = await self.repo.count_orders_by_status(
            seller_id,
            OrderStatus.PROCESSING,
        )

        shipped_orders = await self.repo.count_orders_by_status(
            seller_id,
            OrderStatus.SHIPPED,
        )

        delivered_orders = await self.repo.count_orders_by_status(
            seller_id,
            OrderStatus.DELIVERED,
        )

        cancelled_orders = await self.repo.count_orders_by_status(
            seller_id,
            OrderStatus.CANCELLED,
        )

        total_sales = await self.repo.total_sales(
            seller_id,
        )

        wallet = await self.repo.get_wallet(
            seller_id,
        )

        wallet_balance = (
            Decimal(str(wallet.balance))
            if wallet
            else Decimal("0.00")
        )

        total_earned = (
            Decimal(str(wallet.total_earned))
            if wallet
            else Decimal("0.00")
        )

        total_withdrawn = (
            Decimal(str(wallet.total_withdrawn))
            if wallet
            else Decimal("0.00")
        )

        recent_items = await self.repo.get_vendor_orders(
            seller_id,
            limit=5,
        )

        return VendorDashboardResponse(
            vendor=vendor,
            total_products=total_products,
            active_products=active_products,
            total_orders=total_orders,
            pending_orders=pending_orders,
            processing_orders=processing_orders,
            shipped_orders=shipped_orders,
            delivered_orders=delivered_orders,
            cancelled_orders=cancelled_orders,
            total_sales=total_sales,
            wallet_balance=wallet_balance,
            total_earned=total_earned,
            total_withdrawn=total_withdrawn,
            recent_orders=[
                self.order_item_to_response(item)
                for item in recent_items
            ],
        )
    # ============================================================
    # ADMIN - LIST VENDORS
    # ============================================================

    async def list_vendors(
        self,
        vendor_status: VendorStatus | None = None,
    ):

        return await self.repo.get_all_vendors(
            status=vendor_status,
        )    