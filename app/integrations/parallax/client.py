import httpx

from app.core.config import settings


class ParallaxClient:
    def __init__(self):
        self.base_url = settings.PARALLAX_BASE_URL

        self.headers = {
            "Authorization": f"Bearer {settings.PARALLAX_API_KEY}",
            "Content-Type": "application/json",
        }

    async def get_banks(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/banks",
                headers=self.headers,
            )

        response.raise_for_status()

        return response.json()

    async def create_virtual_account(
        self,
        payload: dict,
    ):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/virtual-accounts",
                headers=self.headers,
                json=payload,
            )

        response.raise_for_status()

        return response.json()

    async def verify_payment(
        self,
        reference: str,
    ):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payments/{reference}",
                headers=self.headers,
            )

        response.raise_for_status()

        return response.json()