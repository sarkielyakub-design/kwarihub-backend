from decimal import Decimal
from enum import Enum
from typing import List

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
    subtotal: Decimal
    shipping_fee: Decimal
    total: Decimal
    status: OrderStatus
    shipping_address: str
    items: List[OrderItemResponse]


class OrderListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    order_number: str
    total: Decimal
    status: OrderStatus
    created_at: str


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class MessageResponse(BaseModel):
    success: bool
    message: str