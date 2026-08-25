import uuid

from fastapi import HTTPException

from app.modules.wallet.repository import WalletRepository
from app.modules.withdrawals.models import (
    Withdrawal,
    WithdrawalStatus,
)
from app.modules.withdrawals.repository import WithdrawalRepository
from app.modules.withdrawals.schemas import (
    CreateWithdrawalRequest,
    ApproveWithdrawalRequest,
    RejectWithdrawalRequest,
)


class WithdrawalService:

    def __init__(
        self,
        withdrawal_repo: WithdrawalRepository,
        wallet_repo: WalletRepository,
    ):
        self.withdrawal_repo = withdrawal_repo
        self.wallet_repo = wallet_repo

    async def create(
        self,
        user_id: int,
        request: CreateWithdrawalRequest,
    ):
        wallet = await self.wallet_repo.get_wallet(user_id)

        if not wallet:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found.",
            )

        if wallet.balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient wallet balance.",
            )

        withdrawal = Withdrawal(
            wallet_id=wallet.id,
            user_id=user_id,
            amount=request.amount,
            reference=str(uuid.uuid4()),
            bank_name=request.bank_name,
            account_name=request.account_name,
            account_number=request.account_number,
            narration=request.narration or "",
            status=WithdrawalStatus.PENDING,
        )

        return await self.withdrawal_repo.create(
            withdrawal,
        )

    async def my_withdrawals(
        self,
        user_id: int,
    ):
        return await self.withdrawal_repo.get_user_withdrawals(
            user_id,
        )

    async def get(
        self,
        user_id: int,
        uuid: str,
    ):
        withdrawal = await self.withdrawal_repo.get_by_uuid(
            uuid,
        )

        if not withdrawal:
            raise HTTPException(
                status_code=404,
                detail="Withdrawal not found.",
            )

        if withdrawal.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        return withdrawal

    async def summary(self):
        return {
            "pending": await self.withdrawal_repo.pending_total(),
            "approved": await self.withdrawal_repo.approved_total(),
            "paid": await self.withdrawal_repo.paid_total(),
            "rejected": await self.withdrawal_repo.rejected_total(),
            "total_withdrawals": await self.withdrawal_repo.total_count(),
        }

    async def approve(
        self,
        uuid: str,
        request: ApproveWithdrawalRequest,
    ):
        withdrawal = await self.withdrawal_repo.get_by_uuid(
            uuid,
        )

        if not withdrawal:
            raise HTTPException(
                status_code=404,
                detail="Withdrawal not found.",
            )

        if withdrawal.status != WithdrawalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Withdrawal already processed.",
            )

        wallet = await self.wallet_repo.get_wallet(
            withdrawal.user_id,
        )

        if wallet.balance < withdrawal.amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient wallet balance.",
            )

        await self.wallet_repo.debit(
            wallet,
            withdrawal.amount,
        )

        withdrawal.status = WithdrawalStatus.APPROVED
        withdrawal.reference = request.reference

        return await self.withdrawal_repo.update(
            withdrawal,
        )

    async def reject(
        self,
        uuid: str,
        request: RejectWithdrawalRequest,
    ):
        withdrawal = await self.withdrawal_repo.get_by_uuid(
            uuid,
        )

        if not withdrawal:
            raise HTTPException(
                status_code=404,
                detail="Withdrawal not found.",
            )

        if withdrawal.status != WithdrawalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Withdrawal already processed.",
            )

        withdrawal.status = WithdrawalStatus.REJECTED
        withdrawal.rejection_reason = request.reason

        return await self.withdrawal_repo.update(
            withdrawal,
        )