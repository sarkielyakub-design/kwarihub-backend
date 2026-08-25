from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.wallet.repository import WalletRepository
from app.modules.withdrawals.repository import WithdrawalRepository
from app.modules.withdrawals.schemas import (
    ApproveWithdrawalRequest,
    CreateWithdrawalRequest,
    RejectWithdrawalRequest,
    WithdrawalResponse,
    WithdrawalSummaryResponse,
)
from app.modules.withdrawals.service import WithdrawalService

router = APIRouter(
    prefix="/withdrawals",
    tags=["Withdrawals"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return WithdrawalService(
        withdrawal_repo=WithdrawalRepository(db),
        wallet_repo=WalletRepository(db),
    )


@router.post(
    "",
    response_model=WithdrawalResponse,
)
async def create_withdrawal(
    request: CreateWithdrawalRequest,
    current_user: User = Depends(get_current_user),
    service: WithdrawalService = Depends(get_service),
):
    return await service.create(
        current_user.id,
        request,
    )


@router.get(
    "",
    response_model=list[WithdrawalResponse],
)
async def my_withdrawals(
    current_user: User = Depends(get_current_user),
    service: WithdrawalService = Depends(get_service),
):
    return await service.my_withdrawals(
        current_user.id,
    )


@router.get(
    "/summary",
    response_model=WithdrawalSummaryResponse,
)
async def withdrawal_summary(
    service: WithdrawalService = Depends(get_service),
):
    return await service.summary()


@router.get(
    "/{uuid}",
    response_model=WithdrawalResponse,
)
async def get_withdrawal(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: WithdrawalService = Depends(get_service),
):
    return await service.get(
        current_user.id,
        uuid,
    )


@router.patch(
    "/{uuid}/approve",
    response_model=WithdrawalResponse,
)
async def approve_withdrawal(
    uuid: str,
    request: ApproveWithdrawalRequest,
    service: WithdrawalService = Depends(get_service),
):
    return await service.approve(
        uuid,
        request,
    )


@router.patch(
    "/{uuid}/reject",
    response_model=WithdrawalResponse,
)
async def reject_withdrawal(
    uuid: str,
    request: RejectWithdrawalRequest,
    service: WithdrawalService = Depends(get_service),
):
    return await service.reject(
        uuid,
        request,
    )