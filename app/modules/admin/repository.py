from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category
from app.modules.orders.models import Order, OrderStatus
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.products.models import Product
from app.modules.reviews.models import Review
from app.modules.roles.models import Role
from app.modules.users.models import User
from app.modules.withdrawals.models import Withdrawal, WithdrawalStatus


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================
    # DASHBOARD COUNTS
    # =========================================================

    async def total_users(self):
        result = await self.db.scalar(
            select(func.count(User.id)).where(
                User.is_deleted == False
            )
        )
        return result or 0

    async def total_sellers(self):
        """
        Count unique, non-deleted users assigned to the vendor role
        through the User.roles many-to-many relationship.
        """
        result = await self.db.scalar(
            select(func.count(func.distinct(User.id)))
            .join(User.roles)
            .where(
                Role.slug == "vendor",
                User.is_deleted == False,
            )
        )
        return result or 0

    async def total_products(self):
        result = await self.db.scalar(
            select(func.count(Product.id)).where(
                Product.is_deleted == False
            )
        )
        return result or 0

    async def total_categories(self):
        result = await self.db.scalar(
            select(func.count(Category.id)).where(
                Category.is_deleted == False
            )
        )
        return result or 0

    async def total_orders(self):
        result = await self.db.scalar(
            select(func.count(Order.id)).where(
                Order.is_deleted == False
            )
        )
        return result or 0

    async def total_payments(self):
        result = await self.db.scalar(
            select(func.count(Payment.id)).where(
                Payment.is_deleted == False
            )
        )
        return result or 0

    async def total_reviews(self):
        result = await self.db.scalar(
            select(func.count(Review.id)).where(
                Review.is_deleted == False
            )
        )
        return result or 0

    async def total_withdrawals(self):
        result = await self.db.scalar(
            select(func.count(Withdrawal.id)).where(
                Withdrawal.is_deleted == False
            )
        )
        return result or 0

    # =========================================================
    # PENDING
    # =========================================================

    async def pending_products(self):
        result = await self.db.scalar(
            select(func.count(Product.id)).where(
                Product.is_active == False,
                Product.is_deleted == False,
            )
        )
        return result or 0

    async def pending_withdrawals(self):
        result = await self.db.scalar(
            select(func.count(Withdrawal.id)).where(
                Withdrawal.status == WithdrawalStatus.PENDING,
                Withdrawal.is_deleted == False,
            )
        )
        return result or 0

    # =========================================================
    # REVENUE
    # =========================================================

    async def total_revenue(self):
        revenue = await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Payment.amount),
                    Decimal("0.00"),
                )
            ).where(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.is_deleted == False,
            )
        )
        return revenue or Decimal("0.00")

    # =========================================================
    # USERS
    # =========================================================

    async def get_users(self):
        result = await self.db.execute(
            select(User)
            .where(User.is_deleted == False)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def get_user(self, uuid: str):
        result = await self.db.execute(
            select(User).where(
                User.uuid == uuid,
                User.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update_user(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # =========================================================
    # SELLERS
    # =========================================================

    async def get_sellers(self):
        """
        Return users assigned to the vendor role through user_roles.
        DISTINCT prevents duplicate users if the role association
        contains multiple matching rows.
        """
        result = await self.db.execute(
            select(User)
            .join(User.roles)
            .where(
                Role.slug == "vendor",
                User.is_deleted == False,
            )
            .distinct()
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()

    async def get_seller(self, uuid: str):
        result = await self.db.execute(
            select(User)
            .join(User.roles)
            .where(
                User.uuid == uuid,
                Role.slug == "vendor",
                User.is_deleted == False,
            )
            .distinct()
        )
        return result.scalar_one_or_none()

    # =========================================================
    # PRODUCTS
    # =========================================================

    async def get_products(self):
        result = await self.db.execute(
            select(Product)
            .where(Product.is_deleted == False)
            .order_by(Product.created_at.desc())
        )
        return result.scalars().all()

    async def get_product(self, uuid: str):
        result = await self.db.execute(
            select(Product).where(
                Product.uuid == uuid,
                Product.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update_product(self, product: Product):
        await self.db.commit()
        await self.db.refresh(product)
        return product

    # =========================================================
    # ORDERS
    # =========================================================

    async def get_orders(self):
        result = await self.db.execute(
            select(Order)
            .where(Order.is_deleted == False)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def get_order(self, uuid: str):
        result = await self.db.execute(
            select(Order).where(
                Order.uuid == uuid,
                Order.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update_order(self, order: Order):
        await self.db.commit()
        await self.db.refresh(order)
        return order

    # =========================================================
    # PAYMENTS
    # =========================================================

    async def get_payments(self):
        result = await self.db.execute(
            select(Payment)
            .where(Payment.is_deleted == False)
            .order_by(Payment.created_at.desc())
        )
        return result.scalars().all()

    async def get_payment(self, uuid: str):
        result = await self.db.execute(
            select(Payment).where(
                Payment.uuid == uuid,
                Payment.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    # =========================================================
    # WITHDRAWALS
    # =========================================================

    async def get_withdrawals(self):
        result = await self.db.execute(
            select(Withdrawal)
            .where(Withdrawal.is_deleted == False)
            .order_by(Withdrawal.created_at.desc())
        )
        return result.scalars().all()

    async def get_withdrawal(self, uuid: str):
        result = await self.db.execute(
            select(Withdrawal).where(
                Withdrawal.uuid == uuid,
                Withdrawal.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update_withdrawal(self, withdrawal: Withdrawal):
        await self.db.commit()
        await self.db.refresh(withdrawal)
        return withdrawal

    # =========================================================
    # REVIEWS
    # =========================================================

    async def get_reviews(self):
        result = await self.db.execute(
            select(Review)
            .where(Review.is_deleted == False)
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_review(self, uuid: str):
        result = await self.db.execute(
            select(Review).where(
                Review.uuid == uuid,
                Review.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def update_review(self, review: Review):
        await self.db.commit()
        await self.db.refresh(review)
        return review

    # =========================================================
    # ANALYTICS
    # =========================================================

    async def completed_orders(self):
        result = await self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status == OrderStatus.DELIVERED,
                Order.is_deleted == False,
            )
        )
        return result or 0

    async def pending_orders(self):
        result = await self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status == OrderStatus.PENDING,
                Order.is_deleted == False,
            )
        )
        return result or 0

    async def revenue(self):
        result = await self.db.scalar(
            select(
                func.coalesce(
                    func.sum(Payment.amount),
                    Decimal("0.00"),
                )
            ).where(
                Payment.status == PaymentStatus.SUCCESS,
                Payment.is_deleted == False,
            )
        )
        return result or Decimal("0.00")