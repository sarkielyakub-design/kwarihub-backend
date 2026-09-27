import base64
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import settings


class MonnifyClient:
    """
    Monnify API client.

    Supports Monnify Sandbox/Test mode.
    """

    def __init__(self):
        self.base_url = settings.MONNIFY_BASE_URL.rstrip("/")
        self.api_key = settings.MONNIFY_API_KEY
        self.secret_key = settings.MONNIFY_SECRET_KEY
        self.contract_code = settings.MONNIFY_CONTRACT_CODE

    async def get_access_token(self) -> str:
        credentials = (
            f"{self.api_key}:{self.secret_key}"
        )

        encoded_credentials = base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                headers=headers,
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Monnify authentication failed "
                f"({response.status_code}): "
                f"{response.text}"
            )

        data = response.json()

        if not data.get("requestSuccessful"):
            raise RuntimeError(
                data.get(
                    "responseMessage",
                    "Unable to authenticate with Monnify.",
                )
            )

        response_body = data.get(
            "responseBody",
            {},
        )

        access_token = response_body.get(
            "accessToken"
        )

        if not access_token:
            raise RuntimeError(
                "Monnify did not return an access token."
            )

        return access_token

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

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/merchant/transactions/init-transaction",
                json=payload,
                headers=headers,
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Monnify transaction initialization failed "
                f"({response.status_code}): "
                f"{response.text}"
            )

        data = response.json()

        if not data.get("requestSuccessful"):
            raise RuntimeError(
                data.get(
                    "responseMessage",
                    "Unable to initialize Monnify transaction.",
                )
            )

        return data.get("responseBody", {})

    async def verify_transaction(
        self,
        payment_reference: str,
    ) -> dict[str, Any]:

        access_token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        params = {
            "paymentReference": payment_reference,
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                f"{self.base_url}/api/v2/merchant/transactions/query",
                params=params,
                headers=headers,
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Monnify verification failed "
                f"({response.status_code}): "
                f"{response.text}"
            )

        data = response.json()

        if not data.get("requestSuccessful"):
            raise RuntimeError(
                data.get(
                    "responseMessage",
                    "Unable to verify Monnify transaction.",
                )
            )

        response_body = data.get(
            "responseBody",
            {},
        )

        if not response_body:
            raise RuntimeError(
                "Monnify returned an empty verification response."
            )

        return response_body