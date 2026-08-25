from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.auth.models import RefreshToken
    from app.modules.bank_accounts.models import BankAccount
    from app.modules.cart.models import CartItem
    from app.modules.notifications.models import Notification
    from app.modules.orders.models import Order
    from app.modules.products.models import Product
    from app.modules.reviews.models import Review
    from app.modules.roles.models import Role
    from app.modules.wallet.models import Wallet
    from app.modules.withdrawals.models import Withdrawal
    from app.modules.wishlist.models import Wishlist
    from app.modules.payments.models import Payment

class User(BaseModel):
    __tablename__ = "users"

    # ==========================
    # Basic Information
    # ==========================

    first_name: Mapped[str] = mapped_column(
        String(100),
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
    )

    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # ==========================
    # Account Status
    # ==========================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==========================
    # Role
    # ==========================

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
    )

    # ==========================
    # Authentication
    # ==========================

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Products
    # ==========================

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="seller",
    )

    # ==========================
    # Wishlist
    # ==========================

    wishlist_items: Mapped[list["Wishlist"]] = relationship(
        "Wishlist",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Cart
    # ==========================

    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Orders
    # ==========================

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="buyer",
    )

    # ==========================
    # Reviews
    # ==========================

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="buyer",
    )

    # ==========================
    # Notifications
    # ==========================

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Wallet
    # ==========================

    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
    )

    # ==========================
    # Withdrawals
    # ==========================

    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        "Withdrawal",
        back_populates="user",
    )

    # ==========================
    # Bank Accounts
    # ==========================

    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Payment
    # ==========================

    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        uselist=False,
    )