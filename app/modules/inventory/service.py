from fastapi import HTTPException

from app.modules.inventory.repository import InventoryRepository


class InventoryService:

    def __init__(
        self,
        repo: InventoryRepository,
    ):
        self.repo = repo

    async def list_inventory(
        self,
        seller_id: int,
    ):
        return await self.repo.get_all(
            seller_id,
        )

    async def update_quantity(
        self,
        seller_id: int,
        variant_uuid: str,
        quantity: int,
    ):
        variant = await self.repo.get_variant(
            variant_uuid,
            seller_id,
        )

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found.",
            )

        variant.quantity = quantity

        return await self.repo.update(
            variant,
        )

    async def add_stock(
        self,
        seller_id: int,
        variant_uuid: str,
        quantity: int,
    ):
        variant = await self.repo.get_variant(
            variant_uuid,
            seller_id,
        )

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found.",
            )

        variant.quantity += quantity

        return await self.repo.update(
            variant,
        )