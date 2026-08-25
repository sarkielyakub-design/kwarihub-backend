from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict


class SellerOrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class SellerOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    product_name: str
    variant_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class SellerOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_uuid: str
    order_number: str
    buyer_name: str
    shipping_address: str
    status: SellerOrderStatus
    created_at: datetime
    items: List[SellerOrderItemResponse]


class UpdateSellerOrderStatusRequest(BaseModel):
    status: SellerOrderStatus