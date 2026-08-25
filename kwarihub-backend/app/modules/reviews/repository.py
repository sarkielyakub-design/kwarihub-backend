from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.order_items.models import OrderItem
from app.modules.products.models import Product
from app.modules.reviews.models import Review


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, review: Review):
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_by_uuid(self, uuid: str):
        result = await self.db.execute(
            select(Review)
            .options(
                selectinload(Review.product),
                selectinload(Review.buyer),
            )
            .where(
                Review.uuid == uuid,
                Review.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_order_item(self, order_item_id: int):
        result = await self.db.execute(
            select(Review).where(
                Review.order_item_id == order_item_id,
                Review.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_product_reviews(self, product_id: int):
        result = await self.db.execute(
            select(Review)
            .options(
                selectinload(Review.buyer),
            )
            .where(
                Review.product_id == product_id,
                Review.is_deleted == False,
            )
            .order_by(
                Review.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def get_seller_reviews(self, seller_id: int):
        result = await self.db.execute(
            select(Review)
            .join(Product)
            .options(
                selectinload(Review.product),
                selectinload(Review.buyer),
            )
            .where(
                Product.seller_id == seller_id,
                Review.is_deleted == False,
            )
            .order_by(
                Review.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def get_summary(self, product_id: int):
        avg_rating = await self.db.scalar(
            select(func.avg(Review.rating))
            .where(
                Review.product_id == product_id,
                Review.is_deleted == False,
            )
        )

        total_reviews = await self.db.scalar(
            select(func.count(Review.id))
            .where(
                Review.product_id == product_id,
                Review.is_deleted == False,
            )
        )

        stars = {}

        for star in range(1, 6):
            stars[star] = await self.db.scalar(
                select(func.count(Review.id))
                .where(
                    Review.product_id == product_id,
                    Review.rating == star,
                    Review.is_deleted == False,
                )
            ) or 0

        return {
            "average_rating": round(float(avg_rating or 0), 1),
            "total_reviews": total_reviews or 0,
            "five_star": stars[5],
            "four_star": stars[4],
            "three_star": stars[3],
            "two_star": stars[2],
            "one_star": stars[1],
        }

    async def update(self, review: Review):
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review: Review):
        review.is_deleted = True
        await self.db.commit()