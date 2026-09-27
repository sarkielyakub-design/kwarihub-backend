from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WalletTransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class WalletTransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal


class WalletTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    reference: str
    type: WalletTransactionType
    status: WalletTransactionStatus
    amount: Decimal
    description: str
    created_at: datetime


class CreditWalletRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: str


class DebitWalletRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: str


class WalletSummaryResponse(BaseModel):
    balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal
    total_transactions: int