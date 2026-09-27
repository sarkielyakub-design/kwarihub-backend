from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.products.models import Product
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.cart.models import CartItem

class ProductVariant(BaseModel):
    __tablename__ = "product_variants"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    color: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    size: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    material: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="variants",
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
    "CartItem",
    back_populates="variant",
    cascade="all, delete-orphan",
)