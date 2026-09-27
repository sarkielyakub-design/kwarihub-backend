from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.products.models import Product
    from app.modules.users.models import User
    from app.modules.order_items.models import OrderItem


class Review(BaseModel):
    __tablename__ = "reviews"

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id"),
        nullable=False,
        unique=True,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
    )

    comment: Mapped[str] = mapped_column(
        Text,
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="reviews",
    )

    buyer: Mapped["User"] = relationship(
        "User",
    )

    order_item: Mapped["OrderItem"] = relationship(
        "OrderItem",
    )
    is_verified_purchase: Mapped[bool] = mapped_column(
    default=True,
)