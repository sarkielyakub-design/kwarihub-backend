from sqlalchemy import Boolean
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base_model import BaseModel


class MarketplaceSettings(BaseModel):
    __tablename__ = "marketplace_settings"

    marketplace_name: Mapped[str] = mapped_column(
        String(255),
        default="KWARIHUB",
    )

    support_email: Mapped[str] = mapped_column(
        String(255),
    )

    support_phone: Mapped[str] = mapped_column(
        String(50),
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="NGN",
    )

    commission_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=5.00,
    )

    vat_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=7.50,
    )

    maintenance_mode: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    allow_seller_registration: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    default_shipping_fee: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0,
    )

    payment_provider: Mapped[str] = mapped_column(
        String(50),
        default="PARALLAX",
    )