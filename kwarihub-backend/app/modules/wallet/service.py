from decimal import Decimal
import uuid

from fastapi import HTTPException

from app.core.cache.cache import cache
from app.core.cache.keys import CacheKeys
from app.modules.wallet.models import (
    Wallet,
    WalletTransaction,
    WalletTransactionStatus,
    WalletTransactionType,
)
from app.modules.wallet.repository import WalletRepository
from app.modules.wallet.schemas import (
    CreditWalletRequest,
    DebitWalletRequest,
)


class WalletService:

    def __init__(
        self,
        repo: WalletRepository,
    ):
        self.repo = repo

    async def get_wallet(
        self,
        user_id: int,
    ):
        return await cache.remember(
            key=CacheKeys.WALLET.format(user_id),
            callback=lambda: self._get_wallet(user_id),
            ttl=30,
        )

    async def _get_wallet(
        self,
        user_id: int,
    ):
        wallet = await self.repo.get_wallet(user_id)

        if not wallet:
            wallet = Wallet(
                user_id=user_id,
                balance=Decimal("0.00"),
                total_earned=Decimal("0.00"),
                total_withdrawn=Decimal("0.00"),
            )

            wallet = await self.repo.create_wallet(wallet)

        return wallet

    async def transactions(
        self,
        user_id: int,
    ):
        wallet = await self.get_wallet(user_id)

        return await self.repo.get_transactions(
            wallet.id,
        )

    async def transaction(
        self,
        user_id: int,
        uuid: str,
    ):
        wallet = await self.get_wallet(user_id)

        transaction = await self.repo.get_transaction(uuid)

        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found.",
            )

        if transaction.wallet_id != wallet.id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        return transaction

    async def credit(
        self,
        user_id: int,
        request: CreditWalletRequest,
    ):
        wallet = await self._get_wallet(user_id)

        await self.repo.credit(
            wallet,
            request.amount,
        )

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            reference=str(uuid.uuid4()),
            type=WalletTransactionType.CREDIT,
            status=WalletTransactionStatus.SUCCESS,
            amount=request.amount,
            description=request.description,
        )

        await self.repo.create_transaction(
            transaction,
        )

        await cache.delete(
            CacheKeys.WALLET.format(user_id),
        )

        return wallet

    async def debit(
        self,
        user_id: int,
        request: DebitWalletRequest,
    ):
        wallet = await self._get_wallet(user_id)

        if wallet.balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient wallet balance.",
            )

        await self.repo.debit(
            wallet,
            request.amount,
        )

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            reference=str(uuid.uuid4()),
            type=WalletTransactionType.DEBIT,
            status=WalletTransactionStatus.SUCCESS,
            amount=request.amount,
            description=request.description,
        )

        await self.repo.create_transaction(
            transaction,
        )

        await cache.delete(
            CacheKeys.WALLET.format(user_id),
        )

        return wallet

    async def summary(
        self,
        user_id: int,
    ):
        return await cache.remember(
            key=f"wallet:{user_id}:summary",
            callback=lambda: self._summary(user_id),
            ttl=30,
        )

    async def _summary(
        self,
        user_id: int,
    ):
        wallet = await self._get_wallet(user_id)

        total_transactions = await self.repo.total_transactions(
            wallet.id,
        )

        return {
            "balance": wallet.balance,
            "total_earned": wallet.total_earned,
            "total_withdrawn": wallet.total_withdrawn,
            "total_transactions": total_transactions,
        }