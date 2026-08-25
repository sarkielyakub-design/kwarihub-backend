from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bank_accounts.models import BankAccount


class BankAccountRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        bank_account: BankAccount,
    ):
        self.db.add(bank_account)
        await self.db.commit()
        await self.db.refresh(bank_account)
        return bank_account

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        result = await self.db.execute(
            select(BankAccount).where(
                BankAccount.uuid == uuid,
                BankAccount.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def get_user_accounts(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(BankAccount)
            .where(
                BankAccount.user_id == user_id,
                BankAccount.is_deleted == False,
            )
            .order_by(
                BankAccount.is_default.desc(),
                BankAccount.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def get_default(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(BankAccount).where(
                BankAccount.user_id == user_id,
                BankAccount.is_default == True,
                BankAccount.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    async def clear_default(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(BankAccount).where(
                BankAccount.user_id == user_id,
                BankAccount.is_default == True,
                BankAccount.is_deleted == False,
            )
        )

        accounts = result.scalars().all()

        for account in accounts:
            account.is_default = False

        await self.db.flush()

    async def update(
        self,
        bank_account: BankAccount,
    ):
        await self.db.commit()
        await self.db.refresh(bank_account)
        return bank_account

    async def delete(
        self,
        bank_account: BankAccount,
    ):
        bank_account.is_deleted = True
        await self.db.commit()