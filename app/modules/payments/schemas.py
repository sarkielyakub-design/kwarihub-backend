from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ============================================================
# INITIALIZE PAYMENT
# ============================================================

class InitializePaymentRequest(BaseModel):
    amount: Decimal
    customer_name: str
    customer_email: EmailStr
    payment_reference: str
    payment_description: str = "KWARIHUB Order Payment"
    redirect_url: str


class InitializePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_reference: str
    checkout_url: str
    transaction_reference: str
    amount: Decimal
    currency: str


# ============================================================
# VERIFY PAYMENT
# ============================================================

class VerifyPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_uuid: str
    order_uuid: str
    order_number: str

    payment_reference: str
    transaction_reference: Optional[str] = None

    amount: Optional[Decimal] = None
    currency: Optional[str] = None

    payment_status: str
    payment_method: Optional[str] = None

    order_status: str