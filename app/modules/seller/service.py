from decimal import Decimal

from app.core.cache.cache import cache
from app.core.cache.keys import CacheKeys
from app.modules.orders.models import OrderStatus
from app.modules.seller.repository import SellerRepository


class SellerService:

    def __init__(
        self,
        repo: SellerRepository,
    ):
        self.repo = repo

    async def dashboard(
        self,
        seller_id: int,
    ):
        return await cache.remember(
            key=CacheKeys.SELLER_DASHBOARD.format(seller_id),
            callback=lambda: self._build_dashboard(seller_id),
            ttl=60,
        )

    async def _build_dashboard(
        self,
        seller_id: int,
    ):
        return {
            "total_products":
                await self.repo.total_products(seller_id),

            "active_products":
                await self.repo.active_products(seller_id),

            "total_orders":
                await self.repo.total_orders(seller_id),

            "pending_orders":
                await self.repo.orders_by_status(
                    seller_id,
                    OrderStatus.PENDING,
                ),

            "processing_orders":
                await self.repo.orders_by_status(
                    seller_id,
                    OrderStatus.PROCESSING,
                ),

            "shipped_orders":
                await self.repo.orders_by_status(
                    seller_id,
                    OrderStatus.SHIPPED,
                ),

            "delivered_orders":
                await self.repo.orders_by_status(
                    seller_id,
                    OrderStatus.DELIVERED,
                ),

            "total_sales":
                await self.repo.total_sales(seller_id),

            "today_sales":
                Decimal("0.00"),

            "total_customers":
                0,

            "average_rating":
                0,

            "out_of_stock_products":
                await self.repo.out_of_stock(seller_id),
        }

    async def clear_dashboard_cache(
        self,
        seller_id: int,
    ):
        await cache.delete(
            CacheKeys.SELLER_DASHBOARD.format(seller_id),
        )