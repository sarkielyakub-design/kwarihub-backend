from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cart.models import CartItem
from app.modules.categories.models import Category
from app.modules.notifications.models import Notification
from app.modules.orders.models import Order, OrderStatus
from app.modules.product_images.models import ProductImage
from app.modules.products.models import Product
from app.modules.users.models import User
from app.modules.wallet.models import Wallet
from app.modules.wishlist.models import Wishlist


class DashboardRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================================================
    # USER
    # ==========================================================

    async def get_user(self, user_id: int):
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # WALLET
    # ==========================================================

    async def get_wallet(self, user_id: int):
        result = await self.db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # CART COUNT
    # ==========================================================

    async def get_cart_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(CartItem.quantity),
                    0,
                )
            ).where(
                CartItem.user_id == user_id,
                CartItem.is_deleted == False,
            )
        )

        return int(result.scalar() or 0)

    # ==========================================================
    # WISHLIST COUNT
    # ==========================================================

    async def get_wishlist_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Wishlist.id)).where(
                Wishlist.user_id == user_id,
                Wishlist.is_deleted == False,
            )
        )

        return int(result.scalar() or 0)

    # ==========================================================
    # UNREAD NOTIFICATIONS
    # ==========================================================

    async def get_unread_notifications(
        self,
        user_id: int,
    ) -> int:

        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_deleted == False,
            )
        )

        return int(result.scalar() or 0)

    # ==========================================================
    # ORDER STATISTICS
    # ==========================================================

    async def get_order_statistics(self, user_id: int):

        total_orders_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.buyer_id == user_id,
                Order.is_deleted == False,
            )
        )

        pending_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.buyer_id == user_id,
                Order.status == OrderStatus.PENDING,
                Order.is_deleted == False,
            )
        )

        processing_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.buyer_id == user_id,
                Order.status == OrderStatus.PROCESSING,
                Order.is_deleted == False,
            )
        )

        delivered_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.buyer_id == user_id,
                Order.status == OrderStatus.DELIVERED,
                Order.is_deleted == False,
            )
        )

        cancelled_result = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.buyer_id == user_id,
                Order.status == OrderStatus.CANCELLED,
                Order.is_deleted == False,
            )
        )

        spent_result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(Order.total),
                    0,
                )
            ).where(
                Order.buyer_id == user_id,
                Order.status == OrderStatus.PAID,
                Order.is_deleted == False,
            )
        )

        return {
            "total_orders": int(
                total_orders_result.scalar() or 0
            ),
            "pending_orders": int(
                pending_result.scalar() or 0
            ),
            "processing_orders": int(
                processing_result.scalar() or 0
            ),
            "delivered_orders": int(
                delivered_result.scalar() or 0
            ),
            "cancelled_orders": int(
                cancelled_result.scalar() or 0
            ),
            "total_spent": (
                spent_result.scalar()
                or Decimal("0.00")
            ),
        }

    # ==========================================================
    # RECENT ORDERS
    # ==========================================================

    async def get_recent_orders(
        self,
        user_id: int,
        limit: int = 5,
    ):

        result = await self.db.execute(
            select(Order)
            .where(
                Order.buyer_id == user_id,
                Order.is_deleted == False,
            )
            .order_by(
                desc(Order.created_at)
            )
            .limit(limit)
        )

        return result.scalars().all()

    # ==========================================================
    # FEATURED PRODUCTS
    # ==========================================================

    async def get_featured_products(
        self,
        limit: int = 10,
    ):

        result = await self.db.execute(
            select(Product)
            .where(
                Product.is_deleted == False,
                Product.is_active == True,
                Product.is_featured == True,
                Product.status == "active",
            )
            .order_by(
                desc(Product.created_at)
            )
            .limit(limit)
        )

        return result.scalars().all()

    # ==========================================================
    # LATEST PRODUCTS
    # ==========================================================

    async def get_latest_products(
        self,
        limit: int = 10,
    ):

        result = await self.db.execute(
            select(Product)
            .where(
                Product.is_deleted == False,
                Product.is_active == True,
                Product.status == "active",
            )
            .order_by(
                desc(Product.created_at)
            )
            .limit(limit)
        )

        return result.scalars().all()

    # ==========================================================
    # PRIMARY IMAGE
    # ==========================================================

    async def get_primary_image(
        self,
        product_id: int,
    ):

        result = await self.db.execute(
            select(ProductImage.image)
            .where(
                ProductImage.product_id == product_id,
                ProductImage.is_primary == True,
                ProductImage.is_deleted == False,
            )
            .limit(1)
        )

        image = result.scalar_one_or_none()

        if image:
            return image

        # Fallback to first image
        result = await self.db.execute(
            select(ProductImage.image)
            .where(
                ProductImage.product_id == product_id,
                ProductImage.is_deleted == False,
            )
            .order_by(ProductImage.sort_order)
            .limit(1)
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # FEATURED CATEGORIES
    # ==========================================================

    async def get_featured_categories(
        self,
        limit: int = 8,
    ):

        result = await self.db.execute(
            select(Category)
            .where(
                Category.is_deleted == False,
                Category.is_active == True,
                Category.is_featured == True,
            )
            .order_by(
                Category.sort_order,
                Category.name,
            )
            .limit(limit)
        )

        return result.scalars().all()