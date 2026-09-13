from decimal import Decimal

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.orders.models import Order, OrderStatus
from app.modules.order_items.models import OrderItem
from app.modules.products.models import Product
from app.modules.product_variants.models import ProductVariant


class SellerRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def total_products(self, seller_id: int):

        result = await self.db.scalar(
            select(func.count(Product.id))
            .where(
                Product.seller_id == seller_id,
                Product.is_deleted == False,
            )
        )

        return result or 0

    async def active_products(self, seller_id: int):

        result = await self.db.scalar(
            select(func.count(Product.id))
            .where(
                Product.seller_id == seller_id,
                Product.is_active == True,
                Product.is_deleted == False,
            )
        )

        return result or 0

    async def total_orders(self, seller_id: int):

        result = await self.db.scalar(
            select(func.count(OrderItem.id))
            .where(
                OrderItem.seller_id == seller_id,
            )
        )

        return result or 0

    async def orders_by_status(
        self,
        seller_id: int,
        status: OrderStatus,
    ):

        result = await self.db.scalar(
            select(func.count(OrderItem.id))
            .join(Order)
            .where(
                OrderItem.seller_id == seller_id,
                Order.status == status,
            )
        )

        return result or 0

    async def total_sales(self, seller_id: int):

        result = await self.db.scalar(
            select(func.coalesce(func.sum(OrderItem.total_price), Decimal("0")))
            .join(Order)
            .where(
                OrderItem.seller_id == seller_id,
                Order.status == OrderStatus.DELIVERED,
            )
        )

        return result or Decimal("0")

    async def out_of_stock(self, seller_id: int):

        result = await self.db.scalar(
            select(func.count(ProductVariant.id))
            .join(Product)
            .where(
                Product.seller_id == seller_id,
                ProductVariant.quantity <= 0,
            )
        )

        return result or 0