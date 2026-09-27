from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateReviewRequest(BaseModel):
    order_item_uuid: str
    rating: int = Field(..., ge=1, le=5)
    title: str
    comment: str


class UpdateReviewRequest(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    rating: int

    title: str

    comment: str

    buyer_name: str

    product_name: str

    created_at: datetime


class ProductReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    buyer_name: str

    rating: int

    title: str

    comment: str

    created_at: datetime


class ReviewSummaryResponse(BaseModel):
    average_rating: float

    total_reviews: int

    five_star: int

    four_star: int

    three_star: int

    two_star: int

    one_star: int