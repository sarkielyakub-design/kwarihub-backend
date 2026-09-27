from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel


if TYPE_CHECKING:
    from app.modules.users.models import User
    from app.modules.withdrawals.models import Withdrawal


class WalletTransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class WalletTransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Wallet(BaseModel):
    __tablename__ = "wallets"

    # ==========================
    # User
    # ==========================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    # ==========================
    # Balance
    # ==========================

    balance: Mapped[float] = mapped_column(
        Numeric(14, 2),
        default=0,
        nullable=False,
    )

    total_earned: Mapped[float] = mapped_column(
        Numeric(14, 2),
        default=0,
        nullable=False,
    )

    total_withdrawn: Mapped[float] = mapped_column(
        Numeric(14, 2),
        default=0,
        nullable=False,
    )

    # ==========================
    # User Relationship
    # ==========================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="wallet",
    )

    # ==========================
    # Withdrawals
    # ==========================

    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        "Withdrawal",
        back_populates="wallet",
    )


class WalletTransaction(BaseModel):
    __tablename__ = "wallet_transactions"

    # ==========================
    # Wallet
    # ==========================

    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=False,
        index=True,
    )

    # ==========================
    # Transaction Information
    # ==========================

    reference: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    type: Mapped[WalletTransactionType] = mapped_column(
        SQLEnum(WalletTransactionType),
        nullable=False,
    )

    status: Mapped[WalletTransactionStatus] = mapped_column(
        SQLEnum(WalletTransactionStatus),
        default=WalletTransactionStatus.SUCCESS,
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ==========================
    # Wallet Relationship
    # ==========================

    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
    )