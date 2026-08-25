from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCreateRequest(BaseModel):
    category_id: int

    name: str = Field(..., min_length=3, max_length=255)

    description: str = Field(..., min_length=10)

    price: Decimal

    discount_price: Optional[Decimal] = None

    quantity: int = Field(..., ge=0)

    unit: str = Field(..., max_length=50)

    brand: Optional[str] = None

    origin: Optional[str] = None

    is_featured: bool = False


class ProductUpdateRequest(BaseModel):
    category_id: Optional[int] = None

    name: Optional[str] = None

    description: Optional[str] = None

    price: Optional[Decimal] = None

    discount_price: Optional[Decimal] = None

    quantity: Optional[int] = None

    unit: Optional[str] = None

    brand: Optional[str] = None

    origin: Optional[str] = None

    status: Optional[str] = None

    is_featured: Optional[bool] = None

    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
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

    discount_price: Optional[Decimal]

    quantity: int

    unit: str

    brand: Optional[str]

    origin: Optional[str]

    status: str

    is_featured: bool

    is_active: bool


class MessageResponse(BaseModel):
    success: bool
    message: str