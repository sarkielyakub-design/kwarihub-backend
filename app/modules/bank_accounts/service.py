
from fastapi import HTTPException

from app.modules.bank_accounts.models import BankAccount
from app.modules.bank_accounts.repository import BankAccountRepository
from app.modules.bank_accounts.schemas import (
    CreateBankAccountRequest,
    ResolveAccountResponse,
)
from app.modules.payments.monnify import MonnifyClient


class BankAccountService:
    def __init__(
        self,
        repo: BankAccountRepository,
        monnify: MonnifyClient,
    ):
        self.repo = repo
        self.monnify = monnify

    async def get_banks(self):
        return await self.monnify.get_banks()

    async def resolve_account(
        self,
        request: CreateBankAccountRequest,
    ) -> ResolveAccountResponse:
        banks = await self.get_banks()

        selected_bank = next(
            (
                bank for bank in banks
                if bank["code"] == request.bank_code
            ),
            None,
        )

        if selected_bank is None:
            raise ValueError(
                "Please select a valid bank from the bank list."
            )

        result = await self.monnify.validate_bank_account(
            account_number=request.account_number,
            bank_code=selected_bank["code"],
        )

        return ResolveAccountResponse(
            account_name=result["account_name"],
            bank_name=result.get("bank_name") or selected_bank["name"],
            account_number=result["account_number"],
            bank_code=result["bank_code"],
        )

    async def create(
        self,
        user_id: int,
        request: CreateBankAccountRequest,
    ):
        # Always verify with Monnify before saving.
        verified = await self.resolve_account(request)

        default_account = await self.repo.get_default(user_id)

        account = BankAccount(
            user_id=user_id,
            bank_code=verified.bank_code,
            bank_name=verified.bank_name,
            account_name=verified.account_name,
            account_number=verified.account_number,
            is_verified=True,
            is_default=default_account is None,
        )

        return await self.repo.create(account)

    async def get_all(self, user_id: int):
        return await self.repo.get_user_accounts(user_id)

    async def get(self, user_id: int, uuid: str):
        account = await self.repo.get_by_uuid(uuid)

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

    async def make_default(self, user_id: int, uuid: str):
        account = await self.get(user_id, uuid)

        await self.repo.clear_default(user_id)
        account.is_default = True

        return await self.repo.update(account)

    async def delete(self, user_id: int, uuid: str):
        account = await self.get(user_id, uuid)

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
