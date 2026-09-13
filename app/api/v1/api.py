from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.categories.router import router as category_router
from app.modules.products.router import router as products_router
from app.modules.product_images.router import (
    router as product_images_router,
)
from app.modules.dashboard.router import (
    router as dashboard_router,
)
from app.modules.product_variants.router import (
    router as product_variants_router,
)
from app.modules.payments.router import (
    router as payments_router,
)
from app.modules.orders.router import router as orders_router
from app.modules.wishlist.router import (
    router as wishlist_router,
)
from app.modules.cart.router import router as cart_router
from app.modules.seller.router import router as seller_router
from app.modules.seller_orders.router import (
    router as seller_orders_router,
)
from app.modules.inventory.router import (
    router as inventory_router,
)
from app.modules.reviews.router import (
    router as reviews_router,
)
from app.modules.notifications.router import (
    router as notifications_router,
)
from app.modules.wallet.router import (
    router as wallet_router,
)
from app.modules.withdrawals.router import (
    router as withdrawals_router,
)
from app.modules.admin.router import (
    router as admin_router,
)
from app.modules.bank_accounts.router import (
    router as bank_accounts_router,
)
from app.modules.settings.router import (
    router as settings_router,
)
from app.modules.audit_logs.router import (
    router as audit_logs_router,
)
from app.modules.otp.router import router as otp_router











api_router = APIRouter()

# Authentication
api_router.include_router(auth_router)

# Users
api_router.include_router(users_router)

# Categories
api_router.include_router(category_router)

# Products
api_router.include_router(products_router)

# Product Images
api_router.include_router(product_images_router)
api_router.include_router(product_variants_router)
api_router.include_router(wishlist_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(seller_router)
api_router.include_router(
    seller_orders_router
)
api_router.include_router(inventory_router)

api_router.include_router(
    reviews_router,
)
api_router.include_router(
    notifications_router
)

api_router.include_router(
    wallet_router,
)

api_router.include_router(
    withdrawals_router,
)
api_router.include_router(
    admin_router,
)

api_router.include_router(
    bank_accounts_router,
)
api_router.include_router(settings_router)
api_router.include_router(audit_logs_router)
api_router.include_router(otp_router)
api_router.include_router(
    dashboard_router,
)
