"""KWARIHUB - vendors - repository.py"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.order_items.models import OrderItem
from app.modules.orders.models import Order, OrderStatus
from app.modules.products.models import Product
from app.modules.vendors.constants import VendorStatus
from app.modules.vendors.models import Vendor
from app.modules.wallet.models import Wallet


class VendorRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ============================================================
    # VENDOR
    # ============================================================

    async def get_by_user_id(
        self,
        user_id: int,
    ) -> Vendor | None:

        result = await self.db.execute(
            select(Vendor).where(
                Vendor.user_id == user_id,
                Vendor.is_deleted.is_(False),
            )
        )

        return result.scalar_one_or_none()

    async def get_by_uuid(
        self,
        vendor_uuid: str,
    ) -> Vendor | None:

        result = await self.db.execute(
            select(Vendor).where(
                Vendor.uuid == vendor_uuid,
                Vendor.is_deleted.is_(False),
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        vendor: Vendor,
    ) -> Vendor:

        self.db.add(vendor)

        await self.db.flush()

        return vendor

    async def update(
        self,
        vendor: Vendor,
    ) -> Vendor:

        await self.db.commit()
        await self.db.refresh(vendor)

        return vendor

    # ============================================================
    # PRODUCTS
    # ============================================================

    async def count_products(
        self,
        seller_id: int,
    ) -> int:

        result = await self.db.scalar(
            select(func.count(Product.id)).where(
                Product.seller_id == seller_id,
                Product.is_deleted.is_(False),
            )
        )

        return int(result or 0)

    async def count_active_products(
        self,
        seller_id: int,
    ) -> int:

        result = await self.db.scalar(
            select(func.count(Product.id)).where(
                Product.seller_id == seller_id,
                Product.is_deleted.is_(False),
                Product.is_active.is_(True),
                Product.status == "active",
            )
        )

        return int(result or 0)

    # ============================================================
    # ORDERS
    # ============================================================

    async def count_orders(
        self,
        seller_id: int,
    ) -> int:

        result = await self.db.scalar(
            select(func.count(OrderItem.id)).where(
                OrderItem.seller_id == seller_id,
                OrderItem.is_deleted.is_(False),
            )
        )

        return int(result or 0)

    async def count_orders_by_status(
        self,
        seller_id: int,
        order_status: OrderStatus,
    ) -> int:

        result = await self.db.scalar(
            select(func.count(OrderItem.id))
            .join(Order, Order.id == OrderItem.order_id)
            .where(
                OrderItem.seller_id == seller_id,
                OrderItem.is_deleted.is_(False),
                Order.status == order_status,
                Order.is_deleted.is_(False),
            )
        )

        return int(result or 0)

    async def total_sales(
        self,
        seller_id: int,
    ) -> Decimal:

        result = await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(OrderItem.total_price),
                    0,
                )
            )
            .join(
                Order,
                Order.id == OrderItem.order_id,
            )
            .where(
                OrderItem.seller_id == seller_id,
                OrderItem.is_deleted.is_(False),
                Order.is_deleted.is_(False),
                Order.status != OrderStatus.CANCELLED,
            )
        )

        return Decimal(str(result or 0))

    async def get_vendor_orders(
        self,
        seller_id: int,
        limit: int = 100,
    ):

        result = await self.db.execute(
            select(OrderItem)
            .options(
                selectinload(OrderItem.order),
            )
            .join(
                Order,
                Order.id == OrderItem.order_id,
            )
            .where(
                OrderItem.seller_id == seller_id,
                OrderItem.is_deleted.is_(False),
                Order.is_deleted.is_(False),
            )
            .order_by(
                Order.created_at.desc(),
            )
            .limit(limit)
        )

        return result.scalars().all()

    async def get_vendor_order_item(
        self,
        seller_id: int,
        item_uuid: str,
    ):

        result = await self.db.execute(
            select(OrderItem)
            .options(
                selectinload(OrderItem.order),
            )
            .where(
                OrderItem.uuid == item_uuid,
                OrderItem.seller_id == seller_id,
                OrderItem.is_deleted.is_(False),
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # WALLET
    # ============================================================

    async def get_wallet(
        self,
        user_id: int,
    ) -> Wallet | None:

        result = await self.db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.is_deleted.is_(False),
            )
        )

        return result.scalar_one_or_none()
    # ============================================================
    # ADMIN - VENDORS
    # ============================================================

    async def get_all_vendors(
        self,
        status: VendorStatus | None = None,
    ) -> list[Vendor]:

        query = select(Vendor).where(
            Vendor.is_deleted.is_(False),
        )

        if status is not None:
            query = query.where(
                Vendor.status == status,
            )

        query = query.order_by(
            Vendor.created_at.desc(),
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_vendor_by_uuid(
        self,
        vendor_uuid: str,
    ) -> Vendor | None:

        result = await self.db.execute(
            select(Vendor).where(
                Vendor.uuid == vendor_uuid,
                Vendor.is_deleted.is_(False),
            )
        )

        return result.scalar_one_or_none()    