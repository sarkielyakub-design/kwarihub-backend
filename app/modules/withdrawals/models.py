from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.bank_accounts.models import BankAccount
    from app.modules.users.models import User
    from app.modules.wallet.models import Wallet


class WithdrawalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class Withdrawal(BaseModel):
    __tablename__ = "withdrawals"

    # ==========================
    # Wallet
    # ==========================

    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=False,
        index=True,
    )

    # ==========================
    # User
    # ==========================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ==========================
    # Withdrawal Information
    # ==========================

    amount: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    reference: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    bank_account_id: Mapped[int] = mapped_column(
        ForeignKey("bank_accounts.id"),
        nullable=False,
    )

    narration: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[WithdrawalStatus] = mapped_column(
        SQLEnum(WithdrawalStatus),
        default=WithdrawalStatus.PENDING,
        nullable=False,
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ==========================
    # Relationships
    # ==========================

    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="withdrawals",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="withdrawals",
    )

    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount",
    )