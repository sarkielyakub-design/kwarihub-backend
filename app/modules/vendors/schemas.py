from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.vendors.constants import VendorStatus


class VendorApplicationRequest(BaseModel):
    business_name: str = Field(
        min_length=2,
        max_length=255,
    )

    business_description: str | None = Field(
        default=None,
        max_length=5000,
    )

    business_phone: str = Field(
        min_length=7,
        max_length=20,
    )

    business_email: EmailStr

    country: str = Field(
        default="Nigeria",
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=100,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    address: str = Field(
        min_length=5,
        max_length=500,
    )


class VendorUpdateRequest(BaseModel):
    business_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    business_description: str | None = Field(
        default=None,
        max_length=5000,
    )

    business_phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )

    business_email: EmailStr | None = None

    country: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    address: str | None = Field(
        default=None,
        min_length=5,
        max_length=500,
    )


class VendorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    uuid: str
    user_id: int

    business_name: str
    business_description: str | None

    business_phone: str
    business_email: EmailStr

    country: str
    state: str
    city: str
    address: str

    status: VendorStatus

    rejection_reason: str | None
    admin_note: str | None

    reviewed_at: datetime | None
    approved_at: datetime | None
    rejected_at: datetime | None
    suspended_at: datetime | None

    created_at: datetime
    updated_at: datetime


class VendorOrderItemResponse(BaseModel):
    uuid: str
    order_uuid: str
    order_number: str

    product_id: int
    product_name: str
    variant_name: str

    quantity: int
    unit_price: Decimal
    total_price: Decimal

    order_status: str
    shipping_address: str

    created_at: datetime


class VendorDashboardResponse(BaseModel):
    vendor: VendorResponse

    total_products: int
    active_products: int

    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int

    total_sales: Decimal

    wallet_balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal

    recent_orders: list[VendorOrderItemResponse]
class VendorRejectRequest(BaseModel):
    rejection_reason: str = Field(
        min_length=3,
        max_length=2000,
    )

    admin_note: str | None = Field(
        default=None,
        max_length=5000,
    )


class VendorSuspendRequest(BaseModel):
    admin_note: str | None = Field(
        default=None,
        max_length=5000,
    )    
class VendorRejectRequest(BaseModel):
    rejection_reason: str = Field(
        min_length=3,
        max_length=2000,
    )

    admin_note: str | None = Field(
        default=None,
        max_length=5000,
    )


class VendorSuspendRequest(BaseModel):
    admin_note: str | None = Field(
        default=None,
        max_length=5000,
    )


class VendorListResponse(BaseModel):
    total: int
    vendors: list[VendorResponse]    