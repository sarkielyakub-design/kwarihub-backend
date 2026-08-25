from fastapi import HTTPException

from app.modules.order_items.models import OrderItem
from app.modules.orders.models import OrderStatus
from app.modules.products.repository import ProductRepository
from app.modules.reviews.models import Review
from app.modules.reviews.repository import ReviewRepository
from app.modules.reviews.schemas import (
    CreateReviewRequest,
    UpdateReviewRequest,
)


class ReviewService:

    def __init__(
        self,
        review_repo: ReviewRepository,
        product_repo: ProductRepository,
    ):
        self.review_repo = review_repo
        self.product_repo = product_repo

    async def create(
        self,
        buyer_id: int,
        request: CreateReviewRequest,
    ):
        order_item = await self.product_repo.db.get(
            OrderItem,
            {"uuid": request.order_item_uuid},
        )

        if not order_item:
            raise HTTPException(
                status_code=404,
                detail="Order item not found.",
            )

        if order_item.buyer_id != buyer_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot review this order.",
            )

        if order_item.order.status != OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=400,
                detail="Only delivered orders can be reviewed.",
            )

        existing = await self.review_repo.get_by_order_item(
            order_item.id,
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Review already exists.",
            )

        review = Review(
            product_id=order_item.product_id,
            buyer_id=buyer_id,
            order_item_id=order_item.id,
            rating=request.rating,
            title=request.title,
            comment=request.comment,
        )

        return await self.review_repo.create(review)

    async def get(
        self,
        uuid: str,
    ):
        review = await self.review_repo.get_by_uuid(uuid)

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found.",
            )

        return review

    async def product_reviews(
        self,
        product_uuid: str,
    ):
        product = await self.product_repo.get_by_uuid(
            product_uuid,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        return await self.review_repo.get_product_reviews(
            product.id,
        )

    async def seller_reviews(
        self,
        seller_id: int,
    ):
        return await self.review_repo.get_seller_reviews(
            seller_id,
        )

    async def summary(
        self,
        product_uuid: str,
    ):
        product = await self.product_repo.get_by_uuid(
            product_uuid,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        return await self.review_repo.get_summary(
            product.id,
        )

    async def update(
        self,
        buyer_id: int,
        uuid: str,
        request: UpdateReviewRequest,
    ):
        review = await self.review_repo.get_by_uuid(uuid)

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found.",
            )

        if review.buyer_id != buyer_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        if request.rating is not None:
            review.rating = request.rating

        if request.title is not None:
            review.title = request.title

        if request.comment is not None:
            review.comment = request.comment

        return await self.review_repo.update(review)

    async def delete(
        self,
        buyer_id: int,
        uuid: str,
    ):
        review = await self.review_repo.get_by_uuid(uuid)

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found.",
            )

        if review.buyer_id != buyer_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        await self.review_repo.delete(review)

        return {
            "success": True,
            "message": "Review deleted successfully.",
        }