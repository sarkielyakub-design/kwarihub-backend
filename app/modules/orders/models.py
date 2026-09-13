from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.order_items.models import OrderItem
    from app.modules.payments.models import Payment
    from app.modules.users.models import User


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(BaseModel):
    __tablename__ = "orders"

    # ==========================
    # Order Information
    # ==========================

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ==========================
    # Pricing
    # ==========================

    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    shipping_fee: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    total: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # ==========================
    # Status
    # ==========================

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
    )

    # ==========================
    # Shipping
    # ==========================

    shipping_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # ==========================
    # Buyer
    # ==========================

    buyer: Mapped["User"] = relationship(
        "User",
        back_populates="orders",
    )

    # ==========================
    # Order Items
    # ==========================

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Payment
    # ==========================

    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )