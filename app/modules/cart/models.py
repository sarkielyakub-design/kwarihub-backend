from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.product_variants.models import ProductVariant


class CartItem(BaseModel):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "variant_id",
            name="uq_cart_user_variant",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="cart_items",
    )

    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="cart_items",
    )