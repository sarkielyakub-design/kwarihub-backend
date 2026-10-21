
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotions.models import Promotion
from app.modules.promotions.schemas import (
    PromotionCreate,
    PromotionUpdate,
)


CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class PromotionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def is_currently_available(promotion: Promotion) -> bool:
        now = datetime.now(timezone.utc)

        if not promotion.is_active or promotion.is_deleted:
            return False

        if promotion.starts_at:
            start = promotion.starts_at
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if start > now:
                return False

        if promotion.ends_at:
            end = promotion.ends_at
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            if end <= now:
                return False

        if (
            promotion.usage_limit is not None
            and promotion.usage_count >= promotion.usage_limit
        ):
            return False

        return True

    async def list_admin(self) -> list[Promotion]:
        result = await self.db.execute(
            select(Promotion)
            .where(Promotion.is_deleted.is_(False))
            .order_by(Promotion.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[Promotion]:
        result = await self.db.execute(
            select(Promotion)
            .where(
                Promotion.is_active.is_(True),
                Promotion.is_deleted.is_(False),
            )
            .order_by(Promotion.created_at.desc())
        )
        return [
            promotion
            for promotion in result.scalars().all()
            if self.is_currently_available(promotion)
        ]

    async def get_by_id(
        self,
        promotion_id: int,
        *,
        include_deleted: bool = False,
    ) -> Promotion:
        query = select(Promotion).where(
            Promotion.id == promotion_id
        )

        if not include_deleted:
            query = query.where(Promotion.is_deleted.is_(False))

        promotion = await self.db.scalar(query)

        if promotion is None:
            raise HTTPException(
                status_code=404,
                detail="Promotion not found.",
            )

        return promotion

    async def create(
        self,
        payload: PromotionCreate,
    ) -> Promotion:
        data = payload.model_dump()

        if data.get("coupon_code"):
            data["coupon_code"] = data["coupon_code"].strip().upper()

            existing = await self.db.scalar(
                select(Promotion).where(
                    Promotion.coupon_code == data["coupon_code"],
                    Promotion.is_deleted.is_(False),
                )
            )
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="That coupon code is already in use.",
                )

        promotion = Promotion(**data)
        self.db.add(promotion)

        try:
            await self.db.commit()
            await self.db.refresh(promotion)
        except Exception:
            await self.db.rollback()
            raise

        return promotion

    async def update(
        self,
        promotion_id: int,
        payload: PromotionUpdate,
    ) -> Promotion:
        promotion = await self.get_by_id(promotion_id)
        changes = payload.model_dump(exclude_unset=True)

        if "coupon_code" in changes and changes["coupon_code"]:
            changes["coupon_code"] = changes["coupon_code"].strip().upper()

            existing = await self.db.scalar(
                select(Promotion).where(
                    Promotion.coupon_code == changes["coupon_code"],
                    Promotion.id != promotion_id,
                    Promotion.is_deleted.is_(False),
                )
            )
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="That coupon code is already in use.",
                )

        for field, value in changes.items():
            setattr(promotion, field, value)

        # Validate the effective schedule after applying changes.
        if promotion.starts_at and promotion.ends_at:
            start = promotion.starts_at
            end = promotion.ends_at
            if start >= end:
                raise HTTPException(
                    status_code=422,
                    detail="ends_at must be later than starts_at.",
                )

        if promotion.discount_type == "percentage":
            if (
                promotion.discount_value is None
                or promotion.discount_value <= 0
                or promotion.discount_value > 100
            ):
                raise HTTPException(
                    status_code=422,
                    detail="Percentage discount must be greater than 0 and at most 100.",
                )

        if promotion.promotion_type in {"discount", "coupon"}:
            if not promotion.discount_type or promotion.discount_value is None:
                raise HTTPException(
                    status_code=422,
                    detail="Discount promotions require a discount type and value.",
                )

        if promotion.promotion_type == "coupon" and not promotion.coupon_code:
            raise HTTPException(
                status_code=422,
                detail="Coupon promotions require a coupon code.",
            )

        try:
            await self.db.commit()
            await self.db.refresh(promotion)
        except Exception:
            await self.db.rollback()
            raise

        return promotion

    async def publish(self, promotion_id: int) -> Promotion:
        promotion = await self.get_by_id(promotion_id)

        if promotion.promotion_type in {"discount", "coupon"}:
            if not promotion.discount_type or promotion.discount_value is None:
                raise HTTPException(
                    status_code=422,
                    detail="Configure the discount before publishing.",
                )

        if (
            promotion.promotion_type == "coupon"
            and not promotion.coupon_code
        ):
            raise HTTPException(
                status_code=422,
                detail="Configure the coupon code before publishing.",
            )

        promotion.is_active = True
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def pause(self, promotion_id: int) -> Promotion:
        promotion = await self.get_by_id(promotion_id)
        promotion.is_active = False
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def delete(self, promotion_id: int) -> dict:
        promotion = await self.get_by_id(promotion_id)
        promotion.is_active = False
        promotion.is_deleted = True
        await self.db.commit()

        return {
            "success": True,
            "message": "Promotion deleted.",
        }

    @staticmethod
    def calculate_discount(
        promotion: Promotion,
        eligible_subtotal: Decimal,
    ) -> Decimal:
        if not PromotionService.is_currently_available(promotion):
            raise HTTPException(
                status_code=400,
                detail="This promotion is not currently available.",
            )

        if promotion.promotion_type not in {"discount", "coupon"}:
            raise HTTPException(
                status_code=400,
                detail="This promotion does not provide a discount.",
            )

        subtotal = money(eligible_subtotal)

        if subtotal < Decimal(promotion.minimum_order_amount):
            raise HTTPException(
                status_code=400,
                detail="The minimum order amount has not been reached.",
            )

        value = Decimal(promotion.discount_value or 0)

        if promotion.discount_type == "percentage":
            discount = subtotal * value / Decimal("100")
        elif promotion.discount_type == "fixed":
            discount = value
        else:
            raise HTTPException(
                status_code=422,
                detail="Invalid discount configuration.",
            )

        if promotion.maximum_discount_amount is not None:
            discount = min(
                discount,
                Decimal(promotion.maximum_discount_amount),
            )

        return min(money(discount), subtotal)
