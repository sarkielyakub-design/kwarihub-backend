from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr


class SettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    marketplace_name: str

    support_email: EmailStr

    support_phone: str

    currency: str

    commission_percentage: Decimal

    vat_percentage: Decimal

    maintenance_mode: bool

    allow_seller_registration: bool

    default_shipping_fee: Decimal

    payment_provider: str

    created_at: datetime

    updated_at: datetime


class UpdateSettingsRequest(BaseModel):
    marketplace_name: str

    support_email: EmailStr

    support_phone: str

    currency: str

    commission_percentage: Decimal

    vat_percentage: Decimal

    maintenance_mode: bool

    allow_seller_registration: bool

    default_shipping_fee: Decimal

    payment_provider: str