from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.wallet.models import (
    Wallet,
    WalletTransaction,
)


class WalletRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_wallet(
        self,
        wallet: Wallet,
    ):
        self.db.add(wallet)
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet

    async def create_transaction(
        self,
        transaction: WalletTransaction,
    ):
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_wallet(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(Wallet)
            .options(
                selectinload(Wallet.user),
            )
            .where(
                Wallet.user_id == user_id,
                Wallet.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_transactions(
        self,
        wallet_id: int,
    ):
        result = await self.db.execute(
            select(WalletTransaction)
            .where(
                WalletTransaction.wallet_id == wallet_id,
                WalletTransaction.is_deleted == False,
            )
            .order_by(
                WalletTransaction.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def get_transaction(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(WalletTransaction)
            .where(
                WalletTransaction.uuid == uuid,
                WalletTransaction.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def total_transactions(
        self,
        wallet_id: int,
    ):
        result = await self.db.scalar(
            select(
                func.count(
                    WalletTransaction.id
                )
            ).where(
                WalletTransaction.wallet_id == wallet_id,
                WalletTransaction.is_deleted == False,
            )
        )

        return result or 0

    async def credit(
        self,
        wallet: Wallet,
        amount: Decimal,
    ):
        wallet.balance += amount
        wallet.total_earned += amount

        await self.db.commit()
        await self.db.refresh(wallet)

        return wallet

    async def debit(
        self,
        wallet: Wallet,
        amount: Decimal,
    ):
        wallet.balance -= amount
        wallet.total_withdrawn += amount

        await self.db.commit()
        await self.db.refresh(wallet)

        return wallet

    async def update_wallet(
        self,
        wallet: Wallet,
    ):
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet