from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.wallet.repository import WalletRepository
from app.modules.wallet.schemas import (
    CreditWalletRequest,
    DebitWalletRequest,
    WalletResponse,
    WalletSummaryResponse,
    WalletTransactionResponse,
)
from app.modules.wallet.service import WalletService

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return WalletService(
        WalletRepository(db),
    )


@router.get(
    "",
    response_model=WalletResponse,
)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_service),
):
    return await service.get_wallet(
        current_user.id,
    )


@router.get(
    "/summary",
    response_model=WalletSummaryResponse,
)
async def wallet_summary(
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_service),
):
    return await service.summary(
        current_user.id,
    )


@router.get(
    "/transactions",
    response_model=list[WalletTransactionResponse],
)
async def wallet_transactions(
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_service),
):
    return await service.transactions(
        current_user.id,
    )


@router.get(
    "/transactions/{uuid}",
    response_model=WalletTransactionResponse,
)
async def wallet_transaction(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_service),
):
    return await service.transaction(
        current_user.id,
        uuid,
    )


@router.post(
    "/credit",
    response_model=WalletResponse,
)
async def credit_wallet(
    request: CreditWalletRequest,
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_service),
):
    return await service.credit(
        current_user.id,
        request,
    )


@router.post(
    "/debit",
    response_model=WalletResponse,
)
async def debit_wallet(
    request: DebitWalletRequest,
    current_user: User = Depends(get_current_user),
    service: WalletService = Depends(get_service),
):
    return await service.debit(
        current_user.id,
        request,
    )