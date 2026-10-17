
from pydantic import BaseModel, ConfigDict, Field


class CreateBankAccountRequest(BaseModel):
    bank_code: str = Field(..., min_length=1, max_length=20)
    account_number: str = Field(
        ...,
        pattern=r"^\d{10}$",
        description="10-digit Nigerian bank account number",
    )


class BankOptionResponse(BaseModel):
    name: str
    code: str


class ResolveAccountResponse(BaseModel):
    account_name: str
    bank_name: str
    account_number: str
    bank_code: str
