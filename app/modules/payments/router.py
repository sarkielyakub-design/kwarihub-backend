"""KWARIHUB - payments - router.py"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.payments.monnify import MonnifyClient
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import (
    InitializePaymentRequest,
    InitializePaymentResponse,
    VerifyPaymentResponse,
)
from app.modules.payments.service import PaymentService
from app.modules.users.models import User


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


# ============================================================
# SERVICE
# ============================================================

def get_payment_service(
    db: AsyncSession = Depends(get_db),
):
    return PaymentService(
        monnify=MonnifyClient(),
        payment_repo=PaymentRepository(db),
    )


# ============================================================
# INITIALIZE PAYMENT
# ============================================================

@router.post(
    "/initialize",
    response_model=InitializePaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def initialize_payment(
    request: InitializePaymentRequest,
    service: PaymentService = Depends(
        get_payment_service
    ),
):
    try:
        return await service.initialize(
            amount=request.amount,
            customer_name=request.customer_name,
            customer_email=request.customer_email,
            payment_reference=request.payment_reference,
            payment_description=request.payment_description,
            redirect_url=request.redirect_url,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )


# ============================================================
# VERIFY PAYMENT
# ============================================================

@router.get(
    "/verify/{payment_reference}",
    response_model=VerifyPaymentResponse,
)
async def verify_payment(
    payment_reference: str,
    service: PaymentService = Depends(
        get_payment_service
    ),
):
    try:
        return await service.verify(
            payment_reference
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )