
"""KWARIHUB - payments - router.py"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.payments.monnify import MonnifyClient
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import VerifyPaymentResponse
from app.modules.payments.service import PaymentService
from app.modules.users.models import User

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_payment_service(
    db: AsyncSession = Depends(get_db),
):
    return PaymentService(
        monnify=MonnifyClient(),
        payment_repo=PaymentRepository(db),
    )


@router.get(
    "/verify/{payment_reference}",
    response_model=VerifyPaymentResponse,
)
async def verify_payment(
    payment_reference: str,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
):
    payment = await service.payment_repo.get_by_reference(
        payment_reference
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to verify this payment.",
        )

    return await service.verify(payment_reference)
