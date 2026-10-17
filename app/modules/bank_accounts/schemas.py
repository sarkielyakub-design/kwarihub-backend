
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateBankAccountRequest(BaseModel):
    bank_code: str = Field(..., min_length=1, max_length=50)
    account_number: str = Field(..., min_length=10, max_length=10)


class UpdateBankAccountRequest(BaseModel):
    is_default: bool = True


class ResolveAccountResponse(BaseModel):
    account_name: str
    bank_name: str
    account_number: str
    bank_code: str


class BankAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    bank_code: str
    bank_name: str
    account_name: str
    account_number: str
    is_default: bool
    is_verified: bool
    created_at: datetime
