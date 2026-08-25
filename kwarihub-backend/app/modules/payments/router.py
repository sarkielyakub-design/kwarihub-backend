from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.orders.repository import OrderRepository
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import (
    BankResponse,
    InitializePaymentRequest,
    RegeneratePaymentRequest,
    PaymentResponse,
    PaymentStatusResponse,
)
from app.modules.payments.service import PaymentService
from app.modules.users.models import User

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return PaymentService(
        payment_repo=PaymentRepository(db),
        order_repo=OrderRepository(db),
    )


@router.get(
    "/banks",
    response_model=list[BankResponse],
)
async def get_banks(
    service: PaymentService = Depends(get_service),
):
    return await service.get_banks()


@router.post(
    "/initialize",
    response_model=PaymentResponse,
)
async def initialize_payment(
    request: InitializePaymentRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_service),
):
    return await service.initialize(
        current_user.id,
        request,
    )


@router.post(
    "/regenerate",
    response_model=PaymentResponse,
)
async def regenerate_payment(
    request: RegeneratePaymentRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_service),
):
    return await service.regenerate(
        current_user.id,
        request,
    )


@router.get(
    "/{reference}",
    response_model=PaymentStatusResponse,
)
async def payment_status(
    reference: str,
    service: PaymentService = Depends(get_service),
):
    return await service.status(
        reference,
    )


@router.post("/webhook/parallax")
async def parallax_webhook(
    request: Request,
):
    payload = await request.json()

    # We'll verify the signature and process
    # the payment in the next step.

    return {
        "success": True,
    }