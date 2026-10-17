
import base64
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import settings


class MonnifyClient:
    """
    KwariHub Monnify API client.

    Supports payment initialization, transaction verification,
    bank listing, and bank-account name enquiry.

    API credentials remain on the backend.
    """

    def __init__(self):
        self.base_url = settings.MONNIFY_BASE_URL.rstrip("/")
        self.api_key = settings.MONNIFY_API_KEY
        self.secret_key = settings.MONNIFY_SECRET_KEY
        self.contract_code = settings.MONNIFY_CONTRACT_CODE
        self.timeout = 30.0

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    async def get_access_token(self) -> str:
        credentials = f"{self.api_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                headers=headers,
            )

        if response.is_error:
            raise RuntimeError(
                f"Monnify authentication failed "
                f"({response.status_code})."
            )

        data = response.json()

        if not data.get("requestSuccessful"):
            raise RuntimeError(
                data.get(
                    "responseMessage",
                    "Unable to authenticate with Monnify.",
                )
            )

        access_token = (
            data.get("responseBody") or {}
        ).get("accessToken")

        if not access_token:
            raise RuntimeError(
                "Monnify did not return an access token."
            )

        return str(access_token)

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _check_response(
        response: httpx.Response,
        operation: str,
    ) -> dict[str, Any]:
        if response.is_error:
            raise RuntimeError(
                f"Monnify {operation} failed "
                f"({response.status_code})."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Monnify returned an invalid response during {operation}."
            ) from exc

        if not isinstance(data, dict):
            raise RuntimeError(
                f"Monnify returned an unexpected response during {operation}."
            )

        if not data.get("requestSuccessful"):
            raise RuntimeError(
                str(
                    data.get(
                        "responseMessage",
                        f"Monnify {operation} was unsuccessful.",
                    )
                )
            )

        return data

    # ============================================================
    # INITIALIZE PAYMENT
    # ============================================================

    async def initialize_transaction(
        self,
        *,
        amount: Decimal,
        customer_name: str,
        customer_email: str,
        payment_reference: str,
        payment_description: str,
        redirect_url: str,
    ) -> dict[str, Any]:
        if amount <= Decimal("0"):
            raise ValueError("Payment amount must be greater than zero.")

        access_token = await self.get_access_token()

        payload = {
            "amount": float(amount),
            "customerName": customer_name,
            "customerEmail": str(customer_email),
            "paymentReference": payment_reference,
            "paymentDescription": payment_description,
            "currencyCode": settings.CURRENCY,
            "contractCode": self.contract_code,
            "redirectUrl": redirect_url,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/merchant/transactions/init-transaction",
                json=payload,
                headers=self._auth_headers(access_token),
            )

        data = self._check_response(
            response,
            "transaction initialization",
        )

        body = data.get("responseBody") or {}

        if not isinstance(body, dict) or not body.get("checkoutUrl"):
            raise RuntimeError(
                "Monnify did not return a checkout URL."
            )

        return body

    # ============================================================
    # VERIFY PAYMENT
    # ============================================================

    async def verify_transaction(
        self,
        payment_reference: str,
    ) -> dict[str, Any]:
        if not payment_reference.strip():
            raise ValueError("Payment reference is required.")

        access_token = await self.get_access_token()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v2/merchant/transactions/query",
                params={"paymentReference": payment_reference},
                headers=self._auth_headers(access_token),
            )

        data = self._check_response(
            response,
            "transaction verification",
        )

        body = data.get("responseBody") or {}

        if not isinstance(body, dict) or not body:
            raise RuntimeError(
                "Monnify returned an empty transaction verification response."
            )

        return body

    # ============================================================
    # LIST BANKS
    # ============================================================

    async def get_banks(self) -> list[dict[str, Any]]:
        """
        Return the banks available through the configured Monnify
        environment. The frontend should display names and retain
        bank codes internally.
        """
        access_token = await self.get_access_token()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/banks",
                headers=self._auth_headers(access_token),
            )

        data = self._check_response(response, "bank listing")
        body = data.get("responseBody")

        # Do not silently return an empty list if the provider
        # returns an unexpected response shape.
        if not isinstance(body, list):
            raise RuntimeError(
                "Monnify returned an unexpected bank-list format."
            )

        banks = []

        for bank in body:
            if not isinstance(bank, dict):
                continue

            name = bank.get("name")
            code = bank.get("code")

            if name is None or code is None:
                continue

            name = str(name).strip()
            code = str(code).strip()

            if name and code:
                banks.append({
                    "name": name,
                    "code": code,
                })

        if not banks:
            raise RuntimeError(
                "Monnify returned no usable bank records."
            )

        # Remove duplicates without changing the provider's order.
        unique_banks = []
        seen_codes = set()

        for bank in banks:
            if bank["code"] not in seen_codes:
                seen_codes.add(bank["code"])
                unique_banks.append(bank)

        return unique_banks

    # ============================================================
    # VERIFY BANK ACCOUNT
    # ============================================================

    async def validate_bank_account(
        self,
        *,
        account_number: str,
        bank_code: str,
    ) -> dict[str, str]:
        """
        Resolve a Nigerian bank account through Monnify.

        The returned account name must be used as the verified name.
        Never mark an account verified if name enquiry fails.
        """
        account_number = account_number.strip()
        bank_code = bank_code.strip()

        if not account_number.isdigit() or len(account_number) != 10:
            raise ValueError(
                "Enter a valid 10-digit Nigerian account number."
            )

        if not bank_code:
            raise ValueError("Please select a bank.")

        # Validate the submitted bank code against the current
        # provider bank list before performing account enquiry.
        banks = await self.get_banks()

        selected_bank = next(
            (
                bank for bank in banks
                if bank["code"] == bank_code
            ),
            None,
        )

        if selected_bank is None:
            raise ValueError(
                "The selected bank is not available through Monnify."
            )

        access_token = await self.get_access_token()

        params = {
            "accountNumber": account_number,
            "bankCode": bank_code,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v2/disbursements/account/validate",
                params=params,
                headers=self._auth_headers(access_token),
            )

        data = self._check_response(
            response,
            "bank account verification",
        )

        body = data.get("responseBody") or {}

        if not isinstance(body, dict):
            raise RuntimeError(
                "Monnify returned an invalid account verification response."
            )

        account_name = body.get("accountName")

        if not isinstance(account_name, str) or not account_name.strip():
            raise RuntimeError(
                "Monnify did not return a verified account name."
            )

        verified_account_number = str(
            body.get("accountNumber", account_number)
        )

        verified_bank_code = str(
            body.get("bankCode", bank_code)
        )

        if verified_account_number != account_number:
            raise RuntimeError(
                "The account number returned by Monnify does not match."
            )

        if verified_bank_code != bank_code:
            raise RuntimeError(
                "The bank code returned by Monnify does not match."
            )

        return {
            "account_number": verified_account_number,
            "account_name": account_name.strip(),
            "bank_code": verified_bank_code,
            "bank_name": str(
                body.get("bankName") or selected_bank["name"]
            ).strip(),
        }
