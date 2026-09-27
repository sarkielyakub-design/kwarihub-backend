from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.categories.models import Category
    from app.modules.product_images.models import ProductImage
    from app.modules.product_variants.models import ProductVariant
    from app.modules.reviews.models import Review
    from app.modules.users.models import User
    from app.modules.wishlist.models import Wishlist


class Product(BaseModel):
    __tablename__ = "products"

    # ==========================
    # Foreign Keys
    # ==========================

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    # ==========================
    # Basic Information
    # ==========================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(300),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # ==========================
    # Pricing
    # ==========================

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # ==========================
    # Inventory
    # ==========================

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # ==========================
    # Additional Information
    # ==========================

    brand: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    origin: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    # ==========================
    # Status
    # ==========================

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    is_featured: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # ==========================
    # Seller
    # ==========================

    seller: Mapped["User"] = relationship(
        "User",
        back_populates="products",
    )

    # ==========================
    # Category
    # ==========================

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )

    # ==========================
    # Product Images
    # ==========================

    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Product Variants
    # ==========================

    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Wishlist
    # ==========================

    wishlist_items: Mapped[list["Wishlist"]] = relationship(
        "Wishlist",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    # ==========================
    # Reviews
    # ==========================

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )