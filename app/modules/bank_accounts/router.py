
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.bank_accounts.repository import BankAccountRepository
from app.modules.bank_accounts.schemas import (
    BankAccountResponse,
    CreateBankAccountRequest,
    ResolveAccountResponse,
)
from app.modules.bank_accounts.service import BankAccountService
from app.modules.payments.monnify import MonnifyClient
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
        MonnifyClient(),
    )


# Keep this route BEFORE /{uuid}.
@router.get("/banks")
async def list_banks(
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    try:
        return await service.get_banks()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve banks from Monnify.",
        ) from exc


@router.post(
    "/resolve",
    response_model=ResolveAccountResponse,
)
async def resolve_bank_account(
    request: CreateBankAccountRequest,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    try:
        return await service.resolve_account(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to verify this bank account with Monnify.",
        ) from exc


@router.post(
    "",
    response_model=BankAccountResponse,
)
async def create_bank_account(
    request: CreateBankAccountRequest,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    try:
        return await service.create(current_user.id, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to verify or save the bank account.",
        ) from exc


@router.get(
    "",
    response_model=list[BankAccountResponse],
)
async def my_bank_accounts(
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.get_all(current_user.id)


@router.get(
    "/{uuid}",
    response_model=BankAccountResponse,
)
async def get_bank_account(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.get(current_user.id, uuid)


@router.patch(
    "/{uuid}/default",
    response_model=BankAccountResponse,
)
async def set_default_bank_account(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.make_default(current_user.id, uuid)


@router.delete("/{uuid}")
async def delete_bank_account(
    uuid: str,
    current_user: User = Depends(get_current_user),
    service: BankAccountService = Depends(get_service),
):
    return await service.delete(current_user.id, uuid)
