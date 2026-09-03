from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WishlistProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    image: str
    is_primary: bool
    sort_order: int


class WishlistProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    seller_id: int
    category_id: int

    name: str
    slug: str
    sku: str
    description: str

    price: Decimal
    discount_price: Optional[Decimal] = None

    quantity: int
    unit: str

    brand: Optional[str] = None
    origin: Optional[str] = None

    status: str
    is_featured: bool
    is_active: bool

    images: list[WishlistProductImageResponse] = []


class WishlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    user_id: int
    product_id: int

    product: WishlistProductResponse


class MessageResponse(BaseModel):
    success: bool
    message: str