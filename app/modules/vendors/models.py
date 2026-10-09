"""KWARIHUB - vendors - models.py"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_model import BaseModel
from app.modules.vendors.constants import VendorStatus


if TYPE_CHECKING:
    from app.modules.users.models import User


class Vendor(BaseModel):
    __tablename__ = "vendors"

    # ============================================================
    # USER
    # ============================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # ============================================================
    # BUSINESS INFORMATION
    # ============================================================

    business_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    business_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    business_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    business_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ============================================================
    # ADDRESS
    # ============================================================

    country: Mapped[str] = mapped_column(
        String(100),
        default="Nigeria",
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # ============================================================
    # VENDOR STATUS
    # ============================================================

    status: Mapped[VendorStatus] = mapped_column(
        default=VendorStatus.PENDING,
        nullable=False,
        index=True,
    )

    # ============================================================
    # ADMIN REVIEW
    # ============================================================

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    admin_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    suspended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )