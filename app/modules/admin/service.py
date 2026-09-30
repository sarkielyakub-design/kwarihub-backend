from fastapi import HTTPException

from app.modules.admin.repository import (
    AdminRepository,
)
from app.modules.orders.models import OrderStatus
from app.modules.withdrawals.models import (
    WithdrawalStatus,
)


class AdminService:

    def __init__(
        self,
        repo: AdminRepository,
    ):
        self.repo = repo

    # =========================================================
    # DASHBOARD
    # =========================================================

    async def dashboard(self):
        total_users = (
            await self.repo.total_users()
        )

        total_sellers = (
            await self.repo.total_sellers()
        )

        total_products = (
            await self.repo.total_products()
        )

        total_categories = (
            await self.repo.total_categories()
        )

        total_orders = (
            await self.repo.total_orders()
        )

        total_payments = (
            await self.repo.total_payments()
        )

        total_reviews = (
            await self.repo.total_reviews()
        )

        total_withdrawals = (
            await self.repo.total_withdrawals()
        )

        total_revenue = (
            await self.repo.total_revenue()
        )

        pending_withdrawals = (
            await self.repo.pending_withdrawals()
        )

        pending_products = (
            await self.repo.pending_products()
        )

        return {
            "total_users": total_users,
            "total_sellers": total_sellers,
            "total_products": total_products,
            "total_categories": total_categories,
            "total_orders": total_orders,
            "total_payments": total_payments,
            "total_reviews": total_reviews,
            "total_withdrawals": total_withdrawals,
            "total_revenue": total_revenue,
            "pending_withdrawals":
                pending_withdrawals,
            "pending_products":
                pending_products,
        }

    # =========================================================
    # USERS
    # =========================================================

    async def users(self):
        return await self.repo.get_users()

    async def user(self, uuid: str):
        user = await self.repo.get_user(uuid)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        return user

    async def activate_user(
        self,
        uuid: str,
    ):
        user = await self.user(uuid)

        user.is_active = True

        return await self.repo.update_user(user)

    async def deactivate_user(
        self,
        uuid: str,
    ):
        user = await self.user(uuid)

        user.is_active = False

        return await self.repo.update_user(user)

    async def delete_user(
        self,
        uuid: str,
    ):
        user = await self.user(uuid)

        user.is_deleted = True

        return await self.repo.update_user(user)

    # =========================================================
    # SELLERS
    # =========================================================

    async def sellers(self):
        return await self.repo.get_sellers()

    async def seller(self, uuid: str):
        seller = await self.repo.get_seller(uuid)

        if not seller:
            raise HTTPException(
                status_code=404,
                detail="Seller not found.",
            )

        return seller

    async def verify_seller(
        self,
        uuid: str,
    ):
        seller = await self.seller(uuid)

        seller.is_verified = True

        return await self.repo.update_user(
            seller
        )

    async def suspend_seller(
        self,
        uuid: str,
    ):
        seller = await self.seller(uuid)

        seller.is_active = False

        return await self.repo.update_user(
            seller
        )

    async def activate_seller(
        self,
        uuid: str,
    ):
        seller = await self.seller(uuid)

        seller.is_active = True

        return await self.repo.update_user(
            seller
        )

    # =========================================================
    # PRODUCTS
    # =========================================================

    async def products(self):
        return await self.repo.get_products()

    async def product(self, uuid: str):
        product = await self.repo.get_product(uuid)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        return product

    async def approve_product(
        self,
        uuid: str,
    ):
        product = await self.product(uuid)

        product.is_active = True

        return await self.repo.update_product(
            product
        )

    async def reject_product(
        self,
        uuid: str,
    ):
        product = await self.product(uuid)

        product.is_active = False

        return await self.repo.update_product(
            product
        )

    async def delete_product(
        self,
        uuid: str,
    ):
        product = await self.product(uuid)

        product.is_deleted = True

        return await self.repo.update_product(
            product
        )

    # =========================================================
    # ORDERS
    # =========================================================

    async def orders(self):
        return await self.repo.get_orders()

    async def order(self, uuid: str):
        order = await self.repo.get_order(uuid)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        return order

    async def cancel_order(
        self,
        uuid: str,
    ):
        order = await self.order(uuid)

        order.status = OrderStatus.CANCELLED

        return await self.repo.update_order(
            order
        )

    # =========================================================
    # PAYMENTS
    # =========================================================

    async def payments(self):
        return await self.repo.get_payments()

    async def payment(self, uuid: str):
        payment = await self.repo.get_payment(uuid)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found.",
            )

        return payment

    # =========================================================
    # WITHDRAWALS
    # =========================================================

    async def withdrawals(self):
        return await self.repo.get_withdrawals()

    async def withdrawal(
        self,
        uuid: str,
    ):
        withdrawal = (
            await self.repo.get_withdrawal(uuid)
        )

        if not withdrawal:
            raise HTTPException(
                status_code=404,
                detail="Withdrawal not found.",
            )

        return withdrawal

    async def approve_withdrawal(
        self,
        uuid: str,
    ):
        withdrawal = await self.withdrawal(uuid)

        withdrawal.status = (
            WithdrawalStatus.APPROVED
        )

        return await self.repo.update_withdrawal(
            withdrawal
        )

    async def reject_withdrawal(
        self,
        uuid: str,
        reason: str,
    ):
        withdrawal = await self.withdrawal(uuid)

        withdrawal.status = (
            WithdrawalStatus.REJECTED
        )

        withdrawal.rejection_reason = reason

        return await self.repo.update_withdrawal(
            withdrawal
        )

    async def mark_withdrawal_paid(
        self,
        uuid: str,
    ):
        withdrawal = await self.withdrawal(uuid)

        withdrawal.status = (
            WithdrawalStatus.PAID
        )

        return await self.repo.update_withdrawal(
            withdrawal
        )

    # =========================================================
    # REVIEWS
    # =========================================================

    async def reviews(self):
        return await self.repo.get_reviews()

    async def review(self, uuid: str):
        review = await self.repo.get_review(uuid)

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found.",
            )

        return review

    async def hide_review(
        self,
        uuid: str,
    ):
        review = await self.review(uuid)

        review.is_active = False

        return await self.repo.update_review(
            review
        )

    async def show_review(
        self,
        uuid: str,
    ):
        review = await self.review(uuid)

        review.is_active = True

        return await self.repo.update_review(
            review
        )

    async def delete_review(
        self,
        uuid: str,
    ):
        review = await self.review(uuid)

        review.is_deleted = True

        return await self.repo.update_review(
            review
        )

    # =========================================================
    # ANALYTICS
    # =========================================================

    async def analytics(self):
        total_users = (
            await self.repo.total_users()
        )

        total_sellers = (
            await self.repo.total_sellers()
        )

        total_products = (
            await self.repo.total_products()
        )

        total_orders = (
            await self.repo.total_orders()
        )

        total_completed_orders = (
            await self.repo.completed_orders()
        )

        total_pending_orders = (
            await self.repo.pending_orders()
        )

        total_revenue = (
            await self.repo.revenue()
        )

        return {
            "total_users": total_users,
            "total_sellers": total_sellers,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_completed_orders":
                total_completed_orders,
            "total_pending_orders":
                total_pending_orders,
            "total_revenue": total_revenue,
        }