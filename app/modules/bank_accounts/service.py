from fastapi import HTTPException

from app.modules.bank_accounts.models import BankAccount
from app.modules.bank_accounts.repository import (
    BankAccountRepository,
)
from app.modules.bank_accounts.schemas import (
    CreateBankAccountRequest,
    UpdateBankAccountRequest,
)


class BankAccountService:

    def __init__(
        self,
        repo: BankAccountRepository,
    ):
        self.repo = repo

    async def create(
        self,
        user_id: int,
        request: CreateBankAccountRequest,
    ):
        # TODO:
        # Replace this block with Parallax account
        # resolution when integration is available.

        account = BankAccount(
            user_id=user_id,
            bank_code=request.bank_code,
            bank_name="Parallax Bank",
            account_name="Account Holder",
            account_number=request.account_number,
            is_verified=False,
        )

        default_account = await self.repo.get_default(
            user_id,
        )

        if not default_account:
            account.is_default = True

        return await self.repo.create(account)

    async def get_all(
        self,
        user_id: int,
    ):
        return await self.repo.get_user_accounts(
            user_id,
        )

    async def get(
        self,
        user_id: int,
        uuid: str,
    ):
        account = await self.repo.get_by_uuid(
            uuid,
        )

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Bank account not found.",
            )

        if account.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        return account

    async def make_default(
        self,
        user_id: int,
        uuid: str,
    ):
        account = await self.get(
            user_id,
            uuid,
        )

        await self.repo.clear_default(
            user_id,
        )

        account.is_default = True

        return await self.repo.update(
            account,
        )

    async def delete(
        self,
        user_id: int,
        uuid: str,
    ):
        account = await self.get(
            user_id,
            uuid,
        )

        if account.is_default:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete default bank account.",
            )

        await self.repo.delete(account)

        return {
            "success": True,
            "message": "Bank account deleted successfully.",
        }