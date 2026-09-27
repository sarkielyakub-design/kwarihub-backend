from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException

from app.modules.orders.models import Order, OrderStatus
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.payments.monnify import MonnifyClient
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import (
    InitializePaymentResponse,
    VerifyPaymentResponse,
)


class PaymentService:
    """
    KWARIHUB Payment Service

    Handles:
    - Payment initialization
    - Existing payment reuse
    - Monnify transaction verification
    - Payment status updates
    - Order status synchronization
    - Payment amount validation
    """

    def __init__(
        self,
        monnify: MonnifyClient,
        payment_repo: PaymentRepository,
    ):
        self.monnify = monnify
        self.payment_repo = payment_repo

    # ============================================================
    # INITIALIZE PAYMENT
    # ============================================================

    async def initialize(
        self,
        *,
        order: Order,
        customer_name: str,
        customer_email: str,
        redirect_url: str,
    ) -> InitializePaymentResponse:

        # --------------------------------------------------------
        # VALIDATE ORDER
        # --------------------------------------------------------

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        if order.total is None:
            raise HTTPException(
                status_code=400,
                detail="Order total is missing.",
            )

        order_amount = Decimal(
            str(order.total)
        )

        if order_amount <= Decimal("0.00"):
            raise HTTPException(
                status_code=400,
                detail="Order amount must be greater than zero.",
            )

        # --------------------------------------------------------
        # CHECK EXISTING PAYMENT
        # --------------------------------------------------------

        existing_payment = (
            await self.payment_repo.get_by_order_id(
                order.id
            )
        )

        if existing_payment:

            # ----------------------------------------------------
            # EXISTING PENDING PAYMENT
            # ----------------------------------------------------

            if (
                existing_payment.status
                == PaymentStatus.PENDING
                and existing_payment.checkout_url
            ):
                return InitializePaymentResponse(
                    payment_reference=(
                        existing_payment.reference
                    ),
                    checkout_url=(
                        existing_payment.checkout_url
                    ),
                    transaction_reference=(
                        existing_payment.transaction_reference
                        or ""
                    ),
                    amount=Decimal(
                        str(existing_payment.amount)
                    ),
                    currency=(
                        existing_payment.currency
                    ),
                )

            # ----------------------------------------------------
            # ALREADY PAID
            # ----------------------------------------------------

            if (
                existing_payment.status
                == PaymentStatus.SUCCESS
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "This order has already been paid."
                    ),
                )

        # --------------------------------------------------------
        # GENERATE KWARIHUB PAYMENT REFERENCE
        # --------------------------------------------------------

        payment_reference = (
            f"KWH-{uuid4().hex[:16].upper()}"
        )

        # --------------------------------------------------------
        # PAYMENT EXPIRATION
        # --------------------------------------------------------

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=30)
        )

        # --------------------------------------------------------
        # INITIALIZE TRANSACTION WITH MONNIFY
        # --------------------------------------------------------

        result = (
            await self.monnify.initialize_transaction(
                amount=order_amount,
                customer_name=customer_name,
                customer_email=customer_email,
                payment_reference=payment_reference,
                payment_description=(
                    f"KWARIHUB Order "
                    f"{order.order_number}"
                ),
                redirect_url=redirect_url,
            )
        )

        # --------------------------------------------------------
        # READ MONNIFY RESPONSE
        # --------------------------------------------------------

        checkout_url = result.get(
            "checkoutUrl"
        )

        transaction_reference = result.get(
            "transactionReference"
        )

        if not checkout_url:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Monnify did not return "
                    "a checkout URL."
                ),
            )

        if not transaction_reference:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Monnify did not return "
                    "a transaction reference."
                ),
            )

        # --------------------------------------------------------
        # CREATE LOCAL PAYMENT
        # --------------------------------------------------------

        payment = Payment(
            order_id=order.id,
            user_id=order.buyer_id,
            provider="MONNIFY",
            reference=payment_reference,
            transaction_reference=(
                transaction_reference
            ),
            amount=order_amount,
            currency="NGN",
            status=PaymentStatus.PENDING,
            checkout_url=checkout_url,
            expires_at=expires_at,
        )

        await self.payment_repo.create(
            payment
        )

        # --------------------------------------------------------
        # RESPONSE
        # --------------------------------------------------------

        return InitializePaymentResponse(
            payment_reference=payment_reference,
            checkout_url=checkout_url,
            transaction_reference=(
                transaction_reference
            ),
            amount=order_amount,
            currency="NGN",
        )

    # ============================================================
    # VERIFY PAYMENT
    # ============================================================

    async def verify(
        self,
        payment_reference: str,
    ) -> VerifyPaymentResponse:

        # --------------------------------------------------------
        # VALIDATE REFERENCE
        # --------------------------------------------------------

        if not payment_reference:
            raise HTTPException(
                status_code=400,
                detail="Payment reference is required.",
            )

        # --------------------------------------------------------
        # FIND LOCAL PAYMENT
        #
        # Repository eagerly loads Payment.order.
        # --------------------------------------------------------

        payment = (
            await self.payment_repo.get_by_reference(
                payment_reference
            )
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found.",
            )

        # --------------------------------------------------------
        # GET ASSOCIATED ORDER
        # --------------------------------------------------------

        order = payment.order

        if not order:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Order associated with payment "
                    "was not found."
                ),
            )

        # --------------------------------------------------------
        # ALREADY SUCCESSFUL
        #
        # Avoid calling Monnify repeatedly for a payment
        # that has already been confirmed.
        # --------------------------------------------------------

        if payment.status == PaymentStatus.SUCCESS:

            return VerifyPaymentResponse(
                payment_uuid=str(
                    payment.uuid
                ),
                order_uuid=str(
                    order.uuid
                ),
                order_number=(
                    order.order_number
                ),
                payment_reference=(
                    payment.reference
                ),
                transaction_reference=(
                    payment.transaction_reference
                ),
                amount=Decimal(
                    str(payment.amount)
                ),
                currency=payment.currency,
                payment_status="PAID",
                payment_method=(
                    payment.payment_method
                ),
                order_status=(
                    order.status.value
                ),
            )

        # --------------------------------------------------------
        # CHECK LOCAL EXPIRATION
        # --------------------------------------------------------

        now = datetime.now(
            timezone.utc
        )

        if (
            payment.expires_at
            and payment.expires_at <= now
            and payment.status
            == PaymentStatus.PENDING
        ):
            payment.status = (
                PaymentStatus.EXPIRED
            )

            await self.payment_repo.update(
                payment
            )

            raise HTTPException(
                status_code=400,
                detail="Payment has expired.",
            )

        # --------------------------------------------------------
        # VERIFY WITH MONNIFY
        # --------------------------------------------------------

        result = (
            await self.monnify.verify_transaction(
                payment_reference
            )
        )

        # --------------------------------------------------------
        # READ MONNIFY STATUS
        # --------------------------------------------------------

        payment_status = str(
            result.get(
                "paymentStatus",
                "UNKNOWN",
            )
        ).upper()

        # --------------------------------------------------------
        # READ TRANSACTION REFERENCE
        # --------------------------------------------------------

        transaction_reference = (
            result.get(
                "transactionReference"
            )
        )

        if transaction_reference:
            payment.transaction_reference = (
                transaction_reference
            )

        # --------------------------------------------------------
        # READ PAYMENT METHOD
        # --------------------------------------------------------

        payment_method = (
            result.get(
                "paymentMethod"
            )
        )

        if payment_method:
            payment.payment_method = (
                payment_method
            )

        # --------------------------------------------------------
        # READ MONNIFY AMOUNT
        #
        # IMPORTANT:
        # Monnify verification returns amountPaid.
        # --------------------------------------------------------

        monnify_amount = (
            result.get(
                "amountPaid"
            )
        )

        # --------------------------------------------------------
        # READ CURRENCY
        # --------------------------------------------------------

        monnify_currency = (
            result.get(
                "currencyCode"
            )
        )

        # --------------------------------------------------------
        # VALIDATE AMOUNT
        # --------------------------------------------------------

        if monnify_amount is not None:

            verified_amount = Decimal(
                str(monnify_amount)
            )

            expected_amount = Decimal(
                str(payment.amount)
            )

            if verified_amount != expected_amount:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Payment amount does not "
                        "match the order amount."
                    ),
                )

            payment.amount = (
                verified_amount
            )

        # --------------------------------------------------------
        # UPDATE CURRENCY
        # --------------------------------------------------------

        if monnify_currency:
            payment.currency = (
                monnify_currency
            )

        # --------------------------------------------------------
        # PAID
        # --------------------------------------------------------

        if payment_status == "PAID":

            # Make absolutely sure we have an amount
            # before marking the order as paid.

            if monnify_amount is None:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Monnify did not return "
                        "the amount paid."
                    ),
                )

            verified_amount = Decimal(
                str(monnify_amount)
            )

            expected_amount = Decimal(
                str(order.total)
            )

            if verified_amount != expected_amount:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Verified payment amount "
                        "does not match the order total."
                    ),
                )

            payment.status = (
                PaymentStatus.SUCCESS
            )

            if not payment.paid_at:
                payment.paid_at = (
                    datetime.now(timezone.utc)
                )

            order.status = (
                OrderStatus.PAID
            )

        # --------------------------------------------------------
        # FAILED
        # --------------------------------------------------------

        elif payment_status in (
            "FAILED",
            "CANCELLED",
        ):

            payment.status = (
                PaymentStatus.FAILED
            )

        # --------------------------------------------------------
        # EXPIRED
        # --------------------------------------------------------

        elif payment_status == "EXPIRED":

            payment.status = (
                PaymentStatus.EXPIRED
            )

        # --------------------------------------------------------
        # REVERSED
        # --------------------------------------------------------

        elif payment_status == "REVERSED":

            payment.status = (
                PaymentStatus.FAILED
            )

            # Do not leave an unpaid/reversed transaction
            # marked as paid.

            if order.status == OrderStatus.PAID:
                order.status = (
                    OrderStatus.PENDING
                )

        # --------------------------------------------------------
        # PENDING / PARTIALLY PAID / OVERPAID
        # --------------------------------------------------------

        elif payment_status in (
            "PENDING",
            "PARTIALLY_PAID",
            "OVERPAID",
        ):

            payment.status = (
                PaymentStatus.PENDING
            )

        # --------------------------------------------------------
        # UNKNOWN
        # --------------------------------------------------------

        else:

            payment.status = (
                PaymentStatus.PENDING
            )

        # --------------------------------------------------------
        # SAVE PAYMENT + ORDER
        # --------------------------------------------------------

        await self.payment_repo.update(
            payment
        )

        # --------------------------------------------------------
        # RESPONSE
        # --------------------------------------------------------

        return VerifyPaymentResponse(
            payment_uuid=str(
                payment.uuid
            ),
            order_uuid=str(
                order.uuid
            ),
            order_number=(
                order.order_number
            ),
            payment_reference=(
                payment.reference
            ),
            transaction_reference=(
                payment.transaction_reference
            ),
            amount=(
                Decimal(
                    str(payment.amount)
                )
                if payment.amount is not None
                else None
            ),
            currency=payment.currency,
            payment_status=payment_status,
            payment_method=(
                payment.payment_method
            ),
            order_status=(
                order.status.value
            ),
        )