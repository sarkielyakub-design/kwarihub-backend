from datetime import datetime
from decimal import Decimal
from typing import List
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BankResponse(BaseModel):
    code: str
    name: str


class InitializePaymentRequest(BaseModel):
    order_uuid: str
    preferred_bank: str


class RegeneratePaymentRequest(BaseModel):
    order_uuid: str
    preferred_bank: str


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    reference: str

    bank_code: str
    bank_name: str

    account_name: str
    account_number: str

    amount: Decimal
    currency: str

    status: str

    expires_at: datetime


class PaymentStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    status: str
    amount: Decimal
  

paid_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    success: bool
    message: str