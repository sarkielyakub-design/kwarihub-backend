from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CreateBankAccountRequest(BaseModel):
    bank_code: str
    account_number: str


class UpdateBankAccountRequest(BaseModel):
    is_default: bool = False


class ResolveAccountResponse(BaseModel):
    account_name: str
    bank_name: str
    account_number: str
    bank_code: str


class BankAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    bank_code: str

    bank_name: str

    account_name: str

    account_number: str

    is_default: bool

    is_verified: bool

    created_at: datetime


class BankAccountListResponse(BaseModel):
    accounts: list[BankAccountResponse]


class VerifyBankAccountResponse(BaseModel):
    success: bool

    message: str

    account: Optional[BankAccountResponse] = None