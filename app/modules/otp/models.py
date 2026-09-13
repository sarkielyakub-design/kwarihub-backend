from datetime import datetime, timedelta

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base_model import BaseModel


class OTP(BaseModel):
    __tablename__ = "otps"

    # ==========================
    # User
    # ==========================

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================
    # OTP
    # ==========================

    code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
    )

    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # ==========================
    # Expiration
    # ==========================

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: (
            datetime.utcnow()
            + timedelta(minutes=10)
        ),
        nullable=False,
    )

    # ==========================
    # Status
    # ==========================

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )