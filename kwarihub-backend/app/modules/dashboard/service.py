from fastapi import HTTPException, status

from app.modules.dashboard.repository import (
    DashboardRepository,
)


class DashboardService:

    def __init__(
        self,
        repo: DashboardRepository,
    ):
        self.repo = repo

    async def get_dashboard(
        self,
        user_id: int,
    ):

        # ======================================================
        # USER
        # ======================================================

        user = await self.repo.get_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        # ======================================================
        # WALLET
        # ======================================================

        wallet = await self.repo.get_wallet(user_id)

        # ======================================================
        # COUNTS
        # ======================================================

        cart_count = await self.repo.get_cart_count(
            user_id
        )

        wishlist_count = await self.repo.get_wishlist_count(
            user_id
        )

        unread_notifications = (
            await self.repo.get_unread_notifications(
                user_id
            )
        )

        # ======================================================
        # ORDER STATISTICS
        # ======================================================

        order_stats = (
            await self.repo.get_order_statistics(
                user_id
            )
        )

        # ======================================================
        # RECENT ORDERS
        # ======================================================

        recent_orders = (
            await self.repo.get_recent_orders(
                user_id,
                limit=5,
            )
        )

        # ======================================================
        # PRODUCTS
        # ======================================================

        featured_products = (
            await self.repo.get_featured_products(
                limit=10
            )
        )

        latest_products = (
            await self.repo.get_latest_products(
                limit=10
            )
        )

        # ======================================================
        # CATEGORIES
        # ======================================================

        featured_categories = (
            await self.repo.get_featured_categories(
                limit=8
            )
        )

        # ======================================================
        # PRODUCT IMAGES
        # ======================================================

        product_images = {}

        all_products = (
            featured_products + latest_products
        )

        seen_ids = set()

        for product in all_products:

            if product.id in seen_ids:
                continue

            seen_ids.add(product.id)

            product_images[product.id] = (
                await self.repo.get_primary_image(
                    product.id
                )
            )

        # ======================================================
        # RESPONSE
        # ======================================================

        return {
            "user": {
                "id": user.id,
                "uuid": user.uuid,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "avatar": user.avatar,
            },

            "wallet": {
                "balance": (
                    wallet.balance
                    if wallet
                    else 0
                ),
                "total_earned": (
                    wallet.total_earned
                    if wallet
                    else 0
                ),
                "total_withdrawn": (
                    wallet.total_withdrawn
                    if wallet
                    else 0
                ),
            },

            "stats": {
                "cart_count": cart_count,
                "wishlist_count": wishlist_count,
                "unread_notifications":
                    unread_notifications,

                **order_stats,
            },

            "recent_orders": [
                {
                    "uuid": order.uuid,
                    "order_number": order.order_number,
                    "total": order.total,
                    "shipping_fee": order.shipping_fee,
                    "status": order.status.value
                    if hasattr(order.status, "value")
                    else str(order.status),
                    "created_at": order.created_at,
                }
                for order in recent_orders
            ],

            "featured_products": [
                {
                    "uuid": product.uuid,
                    "name": product.name,
                    "slug": product.slug,
                    "price": product.price,
                    "discount_price":
                        product.discount_price,
                    "quantity": product.quantity,
                    "unit": product.unit,
                    "brand": product.brand,
                    "is_featured":
                        product.is_featured,
                    "image":
                        product_images.get(
                            product.id
                        ),
                }
                for product in featured_products
            ],

            "latest_products": [
                {
                    "uuid": product.uuid,
                    "name": product.name,
                    "slug": product.slug,
                    "price": product.price,
                    "discount_price":
                        product.discount_price,
                    "quantity": product.quantity,
                    "unit": product.unit,
                    "brand": product.brand,
                    "is_featured":
                        product.is_featured,
                    "image":
                        product_images.get(
                            product.id
                        ),
                }
                for product in latest_products
            ],

            "featured_categories": [
                {
                    "uuid": category.uuid,
                    "name": category.name,
                    "slug": category.slug,
                    "description":
                        category.description,
                    "icon": category.icon,
                    "is_featured":
                        category.is_featured,
                }
                for category in featured_categories
            ],
        }