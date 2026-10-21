
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.database.models  # noqa: F401
from app.modules.orders.models import OrderStatus
from app.modules.orders.schemas import CheckoutRequest
from app.modules.orders.service import OrderService


@pytest.mark.asyncio
async def test_checkout_rolls_back_when_payment_initialization_fails(
    monkeypatch,
):
    # Arrange: a valid cart item and product variant.
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

    # No coupon is needed to test the rollback path.
    db = MagicMock()
    db.scalar = AsyncMock(return_value=None)
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
    cart_repo.get_user_cart = AsyncMock(
        return_value=[cart_item]
    )

    variant_repo = MagicMock()
    payment_repo = MagicMock()

    # Simulate a failure from the payment provider/service.
    fake_payment_service = MagicMock()
    fake_payment_service.initialize = AsyncMock(
        side_effect=RuntimeError(
            "Simulated payment initialization failure"
        )
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
    )

    # Act and assert: checkout propagates the payment failure.
    with pytest.raises(
        RuntimeError,
        match="Simulated payment initialization failure",
    ):
        await service.checkout(user, request)

    # The order and its items were attempted before payment failed.
    order_repo.create.assert_awaited_once()
    order_item_repo.create.assert_awaited_once()

    # Rollback must be awaited, and the transaction must not commit.
    db.rollback.assert_awaited_once()
    order_repo.commit.assert_not_awaited()

    # The failure occurred before a coupon redemption was added.
    db.add.assert_not_called()

    # Confirm the payment initialization was attempted.
    fake_payment_service.initialize.assert_awaited_once()

    # The order should have been calculated using server-side prices.
    created_order = order_repo.create.await_args.args[0]
    assert created_order.subtotal == Decimal("20000.00")
    assert created_order.total == Decimal("20000.00")
    assert created_order.status == OrderStatus.PENDING
