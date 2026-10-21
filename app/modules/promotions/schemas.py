
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PromotionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    banner_url: str | None = None

    promotion_type: Literal["banner", "discount", "coupon"] = "banner"
    discount_type: Literal["percentage", "fixed"] | None = None
    discount_value: Decimal | None = Field(default=None, gt=0)
    coupon_code: str | None = Field(default=None, max_length=60)

    product_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)

    minimum_order_amount: Decimal = Field(default=Decimal("0"), ge=0)
    maximum_discount_amount: Decimal | None = Field(default=None, gt=0)
    usage_limit: int | None = Field(default=None, gt=0)

    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @model_validator(mode="after")
    def validate_promotion(self):
        if self.starts_at and self.ends_at:
            if self.ends_at <= self.starts_at:
                raise ValueError("ends_at must be later than starts_at")

        if self.promotion_type in {"discount", "coupon"}:
            if self.discount_type is None or self.discount_value is None:
                raise ValueError(
                    "Discount promotions require discount_type and discount_value"
                )

        if self.discount_type == "percentage":
            if self.discount_value is not None and self.discount_value > 100:
                raise ValueError("Percentage discount cannot exceed 100")

        if self.promotion_type == "coupon" and not self.coupon_code:
            raise ValueError("Coupon promotions require a coupon_code")

        if self.coupon_code:
            self.coupon_code = self.coupon_code.strip().upper()

        return self


class PromotionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    banner_url: str | None = None

    promotion_type: Literal["banner", "discount", "coupon"] | None = None
    discount_type: Literal["percentage", "fixed"] | None = None
    discount_value: Decimal | None = Field(default=None, gt=0)
    coupon_code: str | None = Field(default=None, max_length=60)

    product_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)

    minimum_order_amount: Decimal | None = Field(default=None, ge=0)
    maximum_discount_amount: Decimal | None = Field(default=None, gt=0)
    usage_limit: int | None = Field(default=None, gt=0)

    starts_at: datetime | None = None
    ends_at: datetime | None = None


class PromotionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    title: str
    description: str | None
    banner_url: str | None
    promotion_type: str
    discount_type: str | None
    discount_value: Decimal | None
    coupon_code: str | None
    product_id: int | None
    category_id: int | None
    minimum_order_amount: Decimal
    maximum_discount_amount: Decimal | None
    usage_limit: int | None
    usage_count: int
    starts_at: datetime | None
    ends_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CouponValidationRequest(BaseModel):
    coupon_code: str = Field(min_length=1, max_length=60)
    subtotal: Decimal = Field(gt=0)


class CouponValidationResponse(BaseModel):
    valid: bool
    coupon_code: str
    discount_amount: Decimal
    subtotal: Decimal
    total: Decimal
    message: str
