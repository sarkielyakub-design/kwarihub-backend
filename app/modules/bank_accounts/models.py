from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.users.models import User


class BankAccount(BaseModel):
    __tablename__ = "bank_accounts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    bank_code: Mapped[str] = mapped_column(
        String(20),
    )

    bank_name: Mapped[str] = mapped_column(
        String(100),
    )

    account_name: Mapped[str] = mapped_column(
        String(255),
    )

    account_number: Mapped[str] = mapped_column(
        String(20),
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="bank_accounts",
    )