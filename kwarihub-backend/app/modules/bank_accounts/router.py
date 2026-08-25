from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.bank_accounts.repository import (
    BankAccountRepository,
)
from app.modules.bank_accounts.schemas import (
    BankAccountResponse,
    CreateBankAccountRequest,
    UpdateBankAccountRequest,
)
from app.modules.bank_accounts.service import (
    BankAccountService,
)
from app.modules.users.models import User

router = APIRouter(
    prefix="/bank-accounts",
    tags=["Bank Accounts"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return BankAccountService(
        BankAccountRepository(db),
    )


@router.post(
    "",
    response_model=BankAccountResponse,
)
async def create_bank_account(
    request: CreateBankAccountRequest,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.create(
        current_user.id,
        request,
    )


@router.get(
    "",
    response_model=list[BankAccountResponse],
)
async def my_bank_accounts(
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.get_all(
        current_user.id,
    )


@router.get(
    "/{uuid}",
    response_model=BankAccountResponse,
)
async def get_bank_account(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.get(
        current_user.id,
        uuid,
    )


@router.patch(
    "/{uuid}/default",
    response_model=BankAccountResponse,
)
async def set_default_bank_account(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.make_default(
        current_user.id,
        uuid,
    )


@router.delete(
    "/{uuid}",
)
async def delete_bank_account(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.delete(
        current_user.id,
        uuid,
    )