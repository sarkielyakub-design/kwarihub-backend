"""
KWARIHUB SQLAlchemy model registry.

Importing this module registers all concrete SQLAlchemy
models with app.database.base.Base.metadata.
"""

from app.modules.audit_logs.models import AuditLog
from app.modules.auth.models import RefreshToken
from app.modules.bank_accounts.models import BankAccount
from app.modules.cart.models import CartItem
from app.modules.categories.models import Category
from app.modules.notifications.models import Notification
from app.modules.order_items.models import OrderItem
from app.modules.orders.models import Order
from app.modules.otp.models import OTP
from app.modules.payments.models import Payment
from app.modules.permissions.models import Permission
from app.modules.product_images.models import ProductImage
from app.modules.product_variants.models import ProductVariant
from app.modules.products.models import Product
from app.modules.reviews.models import Review
from app.modules.roles.models import Role
from app.modules.settings.models import MarketplaceSettings
from app.modules.users.models import User
from app.modules.wallet.models import Wallet
from app.modules.wallet.models import WalletTransaction
from app.modules.wishlist.models import Wishlist
from app.modules.withdrawals.models import Withdrawal
