from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# ORDER STATUS
# ============================================================

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# ============================================================
# CHECKOUT REQUEST
# ============================================================

class CheckoutRequest(BaseModel):
    shipping_address: str = Field(
        ...,
        min_length=10,
    )

    redirect_url: str


# ============================================================
# ORDER ITEM RESPONSE
# ============================================================

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    uuid: str
    product_name: str
    variant_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


# ============================================================
# ORDER RESPONSE
# ============================================================

class OrderResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    # Order
    uuid: str
    order_number: str

    # Pricing
    subtotal: Decimal
    shipping_fee: Decimal
    total: Decimal

    # Status
    status: OrderStatus

    # Shipping
    shipping_address: str

    # Items
    items: List[OrderItemResponse]

    # ========================================================
    # PAYMENT
    # ========================================================

    payment_reference: Optional[str] = None

    transaction_reference: Optional[str] = None

    checkout_url: Optional[str] = None

    amount: Optional[Decimal] = None

    currency: Optional[str] = None


# ============================================================
# ORDER LIST RESPONSE
# ============================================================

class OrderListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    uuid: str
    order_number: str
    total: Decimal
    status: OrderStatus
    created_at: str


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


# ============================================================
# GENERIC MESSAGE RESPONSE
# ============================================================

class MessageResponse(BaseModel):
    success: bool
    message: str