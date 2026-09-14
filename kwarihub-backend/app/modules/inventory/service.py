from fastapi import HTTPException

from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import InventoryResponse


class InventoryService:
    def __init__(
        self,
        repo: InventoryRepository,
    ):
        self.repo = repo

    @staticmethod
    def _to_response(variant) -> InventoryResponse:
        return InventoryResponse(
            uuid=str(variant.uuid),
            product_name=variant.product.name,
            sku=variant.sku,
            color=variant.color,
            size=variant.size,
            quantity=variant.quantity,
            price=float(variant.price),
            is_active=variant.is_active,
        )

    async def list_inventory(
        self,
        seller_id: int,
    ):
        variants = await self.repo.get_all(seller_id)

        return [
            self._to_response(variant)
            for variant in variants
        ]

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

        updated_variant = await self.repo.update(variant)

        return self._to_response(updated_variant)

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

        updated_variant = await self.repo.update(variant)

        return self._to_response(updated_variant)