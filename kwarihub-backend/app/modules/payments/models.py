from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.orders.models import Order
    from app.modules.users.models import User


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class Payment(BaseModel):
    __tablename__ = "payments"

    # ============================================================
    # ORDER
    # ============================================================

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    # ============================================================
    # USER
    # ============================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ============================================================
    # PAYMENT PROVIDER
    # ============================================================

    provider: Mapped[str] = mapped_column(
        String(50),
        default="MONNIFY",
        nullable=False,
    )

    # ============================================================
    # KWARIHUB PAYMENT REFERENCE
    # ============================================================

    reference: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    # ============================================================
    # MONNIFY TRANSACTION REFERENCE
    # ============================================================

    transaction_reference: Mapped[Optional[str]] = mapped_column(
        String(150),
        unique=True,
        nullable=True,
        index=True,
    )

    # ============================================================
    # AMOUNT
    # ============================================================

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # ============================================================
    # CURRENCY
    # ============================================================

    currency: Mapped[str] = mapped_column(
        String(10),
        default="NGN",
        nullable=False,
    )

    # ============================================================
    # STATUS
    # ============================================================

    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    # ============================================================
    # MONNIFY CHECKOUT URL
    # ============================================================

    checkout_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # PAYMENT METHOD
    # ============================================================

    payment_method: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ============================================================
    # EXPIRY
    # ============================================================

    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ============================================================
    # PAID AT
    # ============================================================

    paid_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ============================================================
    # WEBHOOK PAYLOAD
    # ============================================================

    webhook_payload: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # ORDER RELATIONSHIP
    # ============================================================

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="payment",
    )

    # ============================================================
    # USER RELATIONSHIP
    #
    # IMPORTANT:
    # User model uses:
    #
    # payment = relationship(
    #     "Payment",
    #     back_populates="user",
    #     uselist=False,
    # )
    #
    # Therefore this MUST use back_populates="payment"
    # ============================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="payment",
    )