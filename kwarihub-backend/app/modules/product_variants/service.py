from uuid import uuid4

from fastapi import HTTPException

from app.modules.products.repository import ProductRepository
from app.modules.product_variants.models import ProductVariant
from app.modules.product_variants.repository import (
    ProductVariantRepository,
)
from app.modules.product_variants.schemas import (
    ProductVariantCreateRequest,
    ProductVariantUpdateRequest,
)


class ProductVariantService:
    def __init__(
        self,
        variant_repo: ProductVariantRepository,
        product_repo: ProductRepository,
    ):
        self.variant_repo = variant_repo
        self.product_repo = product_repo

    async def create(
        self,
        product_uuid: str,
        seller_id: int,
        request: ProductVariantCreateRequest,
    ):
        product = await self.product_repo.get_by_uuid(product_uuid)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        sku = f"VAR-{uuid4().hex[:10].upper()}"

        while await self.variant_repo.get_by_sku(sku):
            sku = f"VAR-{uuid4().hex[:10].upper()}"

        variant = ProductVariant(
            product_id=product.id,
            color=request.color,
            size=request.size,
            material=request.material,
            sku=sku,
            price=request.price,
            quantity=request.quantity,
        )

        return await self.variant_repo.create(variant)

    async def get_product_variants(
        self,
        product_uuid: str,
    ):
        product = await self.product_repo.get_by_uuid(product_uuid)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        return await self.variant_repo.get_product_variants(
            product.id,
        )

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        variant = await self.variant_repo.get_by_uuid(uuid)

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found.",
            )

        return variant

    async def update(
        self,
        uuid: str,
        seller_id: int,
        request: ProductVariantUpdateRequest,
    ):
        variant = await self.variant_repo.get_by_uuid(uuid)

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found.",
            )

        product = await self.product_repo.get_by_id(
            variant.product_id,
        )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        data = request.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(variant, key, value)

        return await self.variant_repo.update(variant)

    async def delete(
        self,
        uuid: str,
        seller_id: int,
    ):
        variant = await self.variant_repo.get_by_uuid(uuid)

        if not variant:
            raise HTTPException(
                status_code=404,
                detail="Variant not found.",
            )

        product = await self.product_repo.get_by_id(
            variant.product_id,
        )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        await self.variant_repo.delete(variant)

        return {
            "success": True,
            "message": "Variant deleted successfully.",
        }