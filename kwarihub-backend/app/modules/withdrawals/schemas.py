from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WithdrawalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class CreateWithdrawalRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)

    bank_name: str

    account_name: str

    account_number: str

    narration: Optional[str] = None


class ApproveWithdrawalRequest(BaseModel):
    reference: str


class RejectWithdrawalRequest(BaseModel):
    reason: str


class WithdrawalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    amount: Decimal

    reference: str

    bank_name: str

    account_name: str

    account_number: str

    narration: str

    status: WithdrawalStatus

    rejection_reason: Optional[str]

    created_at: datetime


class WithdrawalSummaryResponse(BaseModel):
    pending: Decimal

    approved: Decimal

    paid: Decimal

    rejected: Decimal

    total_withdrawals: int