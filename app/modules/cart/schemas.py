from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class AddToCartRequest(BaseModel):
    variant_uuid: str
    quantity: int


class UpdateCartRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    variant_id: int
    quantity: int

    # Product
    product_id: int
    product_uuid: str
    product_name: str
    product_slug: str

    # Product image
    product_image: Optional[str]

    # Variant
    variant_uuid: str
    color: str
    size: str
    material: str
    variant_sku: str

    # Pricing
    unit_price: Decimal
    item_total: Decimal


class CartSummaryResponse(BaseModel):
    items: List[CartItemResponse]
    subtotal: Decimal
    total_items: int


class MessageResponse(BaseModel):
    success: bool
    message: str