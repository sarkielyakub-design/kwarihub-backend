
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.modules.promotions.service import PromotionService


def make_promotion(**overrides):
    values = {
        "id": 44,
        "title": "Test Coupon",
        "promotion_type": "coupon",
        "discount_type": "percentage",
        "discount_value": Decimal("10.00"),
        "coupon_code": "SAVE10",
        "minimum_order_amount": Decimal("0.00"),
        "maximum_discount_amount": None,
        "usage_limit": 100,
        "usage_count": 0,
        "starts_at": None,
        "ends_at": None,
        "is_active": True,
        "is_deleted": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_inactive_promotion_is_unavailable():
    promotion = make_promotion(is_active=False)

    assert PromotionService.is_currently_available(promotion) is False


def test_deleted_promotion_is_unavailable():
    promotion = make_promotion(is_deleted=True)

    assert PromotionService.is_currently_available(promotion) is False


def test_expired_promotion_is_unavailable():
    promotion = make_promotion(
        ends_at=datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    assert PromotionService.is_currently_available(promotion) is False


def test_promotion_at_usage_limit_is_unavailable():
    promotion = make_promotion(
        usage_limit=10,
        usage_count=10,
    )

    assert PromotionService.is_currently_available(promotion) is False


def test_discount_cannot_exceed_eligible_subtotal():
    promotion = make_promotion(
        discount_type="fixed",
        discount_value=Decimal("5000.00"),
    )

    discount = PromotionService.calculate_discount(
        promotion,
        Decimal("1000.00"),
    )

    assert discount == Decimal("1000.00")


def test_maximum_discount_cap_is_respected():
    promotion = make_promotion(
        discount_type="percentage",
        discount_value=Decimal("50.00"),
        maximum_discount_amount=Decimal("200.00"),
    )

    discount = PromotionService.calculate_discount(
        promotion,
        Decimal("1000.00"),
    )

    assert discount == Decimal("200.00")


def test_minimum_order_amount_is_enforced():
    promotion = make_promotion(
        minimum_order_amount=Decimal("5000.00"),
    )

    with pytest.raises(HTTPException) as exc:
        PromotionService.calculate_discount(
            promotion,
            Decimal("4000.00"),
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "The minimum order amount has not been reached."
