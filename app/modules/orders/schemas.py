
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class CheckoutRequest(BaseModel):
    shipping_address: str = Field(..., min_length=10)
    redirect_url: str
    coupon_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=60,
    )

    def normalized_coupon_code(self) -> Optional[str]:
        if not self.coupon_code:
            return None
        return self.coupon_code.strip().upper() or None


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    product_name: str
    variant_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    order_number: str
    created_at: Optional[datetime] = None

    subtotal: Decimal
    discount_amount: Decimal = Decimal("0.00")
    coupon_code: Optional[str] = None
    promotion_id: Optional[int] = None
    shipping_fee: Decimal
    total: Decimal

    status: OrderStatus
    shipping_address: str
    items: List[OrderItemResponse]

    payment_reference: Optional[str] = None
    transaction_reference: Optional[str] = None
    checkout_url: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None


class OrderListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    order_number: str
    total: Decimal
    status: OrderStatus
    created_at: datetime


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class MessageResponse(BaseModel):
    success: bool
    message: str
