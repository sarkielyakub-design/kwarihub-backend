from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductVariantCreateRequest(BaseModel):
    color: str = Field(..., max_length=100)
    size: str = Field(..., max_length=100)
    material: str = Field(..., max_length=150)
    price: Decimal
    quantity: int = Field(..., ge=0)


class ProductVariantUpdateRequest(BaseModel):
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ProductVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    product_id: int
    color: str
    size: str
    material: str
    sku: str
    price: Decimal
    quantity: int
    is_active: bool


class MessageResponse(BaseModel):
    success: bool
    message: str