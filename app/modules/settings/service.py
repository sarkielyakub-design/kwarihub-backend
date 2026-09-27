from app.modules.settings.models import MarketplaceSettings
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.schemas import UpdateSettingsRequest


class SettingsService:

    def __init__(
        self,
        repo: SettingsRepository,
    ):
        self.repo = repo

    async def get(self):
        settings = await self.repo.get()

        if not settings:
            settings = MarketplaceSettings(
                marketplace_name="KWARIHUB",
                support_email="support@kwarihub.com",
                support_phone="+234000000000",
            )

            settings = await self.repo.create(settings)

        return settings

    async def update(
        self,
        request: UpdateSettingsRequest,
    ):
        settings = await self.get()

        settings.marketplace_name = request.marketplace_name
        settings.support_email = request.support_email
        settings.support_phone = request.support_phone
        settings.currency = request.currency
        settings.commission_percentage = request.commission_percentage
        settings.vat_percentage = request.vat_percentage
        settings.maintenance_mode = request.maintenance_mode
        settings.allow_seller_registration = (
            request.allow_seller_registration
        )
        settings.default_shipping_fee = (
            request.default_shipping_fee
        )
        settings.payment_provider = (
            request.payment_provider
        )

        return await self.repo.update(settings)