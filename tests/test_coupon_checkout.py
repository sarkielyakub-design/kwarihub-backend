
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

# Register application models before the ORM configures relationships.
import app.database.models  # noqa: F401
from app.modules.users.models import User  # noqa: F401

from app.modules.orders.models import OrderStatus
from app.modules.orders.schemas import CheckoutRequest
from app.modules.orders.service import OrderService


@pytest.mark.asyncio
async def test_coupon_checkout_calculates_discount_without_live_payment(
    monkeypatch,
):
    # Fake product and variant.
    product = SimpleNamespace(
        id=12,
        name="Test Fabric",
        seller_id=7,
        category_id=3,
        is_active=True,
        is_deleted=False,
    )

    variant = SimpleNamespace(
        id=22,
        product_id=12,
        product=product,
        sku="TEST-FABRIC-001",
        color="Blue",
        size="5 Yards",
        material="Cotton",
        price=Decimal("10000.00"),
        quantity=10,
        is_active=True,
        is_deleted=False,
    )

    cart_item = SimpleNamespace(
        variant=variant,
        quantity=2,
    )

    user = SimpleNamespace(
        id=5,
        first_name="Test",
        last_name="Buyer",
        email="buyer@example.com",
    )

    # Fake promotion: 10% off an eligible order.
    promotion = SimpleNamespace(
        id=44,
        title="Test Coupon",
        promotion_type="coupon",
        discount_type="percentage",
        discount_value=Decimal("10.00"),
        coupon_code="SAVE10",
        product_id=None,
        category_id=None,
        minimum_order_amount=Decimal("0.00"),
        maximum_discount_amount=None,
        usage_limit=100,
        usage_count=0,
        starts_at=None,
        ends_at=None,
        is_active=True,
        is_deleted=False,
    )

    # Fake async database session. No real database connection is used.
    db = MagicMock()
    db.scalar = AsyncMock(return_value=promotion)
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    order_repo = MagicMock()
    order_repo.db = db
    order_repo.create = AsyncMock(
        side_effect=lambda order: setattr(order, "id", 101)
    )
    order_repo.commit = AsyncMock()

    order_item_repo = MagicMock()
    order_item_repo.create = AsyncMock()

    cart_repo = MagicMock()
    cart_repo.get_user_cart = AsyncMock(return_value=[cart_item])

    variant_repo = MagicMock()
    payment_repo = MagicMock()

    # Fake payment response. Monnify is never contacted.
    fake_payment = SimpleNamespace(
        payment_reference="TEST-PAYMENT-REF",
        transaction_reference="TEST-TRANSACTION-REF",
        checkout_url="https://example.invalid/test-checkout",
        amount=Decimal("18000.00"),
        currency="NGN",
    )

    fake_payment_service = MagicMock()
    fake_payment_service.initialize = AsyncMock(
        return_value=fake_payment
    )

    monkeypatch.setattr(
        "app.modules.orders.service.PaymentService",
        lambda **kwargs: fake_payment_service,
    )

    service = OrderService(
        order_repo=order_repo,
        order_item_repo=order_item_repo,
        cart_repo=cart_repo,
        variant_repo=variant_repo,
        payment_repo=payment_repo,
        monnify=MagicMock(),
    )

    request = CheckoutRequest(
        shipping_address="123 Test Street, Kano",
        redirect_url="https://example.invalid/return",
        coupon_code=" save10 ",
    )

    # Act.
    response = await service.checkout(user, request)

    # Assert the arithmetic:
    # 2 x ₦10,000 = ₦20,000 subtotal.
    # 10% discount = ₦2,000.
    # Final payable total = ₦18,000.
    assert response["subtotal"] == Decimal("20000.00")
    assert response["discount_amount"] == Decimal("2000.00")
    assert response["coupon_code"] == "SAVE10"
    assert response["promotion_id"] == 44
    assert response["total"] == Decimal("18000.00")
    assert response["status"] == OrderStatus.PENDING
    assert response["amount"] == Decimal("18000.00")

    # Payment initialization must use the discounted order total.
    fake_payment_service.initialize.assert_awaited_once()
    payment_call = fake_payment_service.initialize.await_args.kwargs

    assert payment_call["order"].total == Decimal("18000.00")

    # Verify promotion usage and redemption staging.
    assert promotion.usage_count == 1

    redemption_objects = [
        call.args[0]
        for call in db.add.call_args_list
        if call.args
    ]

    assert any(
        getattr(item, "promotion_id", None) == 44
        and getattr(item, "order_id", None) == 101
        for item in redemption_objects
    )

    # Checkout commits through the repository and doesn't roll back.
    order_repo.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()
