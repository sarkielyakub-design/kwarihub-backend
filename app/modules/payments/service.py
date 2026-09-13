from fastapi import HTTPException

from app.integrations.parallax.client import ParallaxClient
from app.modules.orders.repository import OrderRepository
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import (
    InitializePaymentRequest,
    RegeneratePaymentRequest,
)


class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        order_repo: OrderRepository,
    ):
        self.payment_repo = payment_repo
        self.order_repo = order_repo
        self.parallax = ParallaxClient()

    async def get_banks(self):
        return await self.parallax.get_banks()

    async def initialize(
        self,
        user_id: int,
        request: InitializePaymentRequest,
    ):
        order = await self.order_repo.get_by_uuid(
            request.order_uuid
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        if order.buyer_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        existing = await self.payment_repo.get_by_order_id(
            order.id
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Payment already initialized.",
            )

        response = await self.parallax.create_virtual_account(
            order=order,
            bank_code=request.preferred_bank,
        )

        payment = Payment(
            order_id=order.id,
            user_id=user_id,
            provider="PARALLAX",
            reference=response["reference"],
            bank_code=response["bank_code"],
            bank_name=response["bank_name"],
            account_name=response["account_name"],
            account_number=response["account_number"],
            amount=order.total,
            currency="NGN",
            status=PaymentStatus.PENDING,
            expires_at=response["expires_at"],
        )

        return await self.payment_repo.create(payment)

    async def regenerate(
        self,
        user_id: int,
        request: RegeneratePaymentRequest,
    ):
        order = await self.order_repo.get_by_uuid(
            request.order_uuid
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        if order.buyer_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        payment = await self.payment_repo.get_by_order_id(
            order.id
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found.",
            )

        payment.status = PaymentStatus.EXPIRED

        await self.payment_repo.update(payment)

        response = await self.parallax.create_virtual_account(
            order=order,
            bank_code=request.preferred_bank,
        )

        new_payment = Payment(
            order_id=order.id,
            user_id=user_id,
            provider="PARALLAX",
            reference=response["reference"],
            bank_code=response["bank_code"],
            bank_name=response["bank_name"],
            account_name=response["account_name"],
            account_number=response["account_number"],
            amount=order.total,
            currency="NGN",
            status=PaymentStatus.PENDING,
            expires_at=response["expires_at"],
        )

        return await self.payment_repo.create(new_payment)

    async def status(
        self,
        reference: str,
    ):
        payment = await self.payment_repo.get_by_reference(
            reference
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found.",
            )

        return payment