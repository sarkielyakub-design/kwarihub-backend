from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.users.models import User


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
    )

    resource: Mapped[str] = mapped_column(
        String(100),
    )

    resource_uuid: Mapped[str] = mapped_column(
        String(100),
    )

    description: Mapped[str] = mapped_column(
        String(500),
    )

    ip_address: Mapped[str] = mapped_column(
        String(50),
    )

    user_agent: Mapped[str] = mapped_column(
        String(500),
    )

    user: Mapped["User"] = relationship(
        "User",
    )