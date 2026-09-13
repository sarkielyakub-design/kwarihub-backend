from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.orders.models import Order
    from app.modules.products.models import Product
    from app.modules.product_variants.models import ProductVariant
    from app.modules.reviews.models import Review
    from app.modules.users.models import User


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    # ==========================
    # Foreign Keys
    # ==========================

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id"),
        nullable=False,
        index=True,
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ==========================
    # Product Snapshot
    # ==========================

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    variant_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ==========================
    # Pricing / Quantity
    # ==========================

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    total_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # ==========================
    # Order
    # ==========================

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )

    # ==========================
    # Review
    # ==========================

    review: Mapped["Review"] = relationship(
        "Review",
        back_populates="order_item",
        uselist=False,
    )