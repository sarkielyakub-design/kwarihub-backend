
from __future__ import annotations

import os
from pathlib import PurePosixPath
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import HTTPException, status
from slugify import slugify

from app.core.cache.cache import cache
from app.core.cache.keys import CacheKeys
from app.modules.categories.repository import CategoryRepository
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
)


PUBLIC_API_BASE_URL = os.getenv(
    "PUBLIC_API_BASE_URL",
    "https://kwarihub-backend-production-ea77.up.railway.app",
).rstrip("/")


def _public_image_url(image_path: str | None) -> str | None:
    """Convert a stored product image path into a public URL."""
    if not image_path:
        return None

    value = image_path.strip()
    if not value:
        return None

    # Support absolute URLs from external image storage.
    if value.startswith(("https://", "http://")):
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return None
        return value

    # Support both /storage/products/file.webp and legacy
    # absolute filesystem paths containing /storage/products/.
    normalized = value.replace("\\", "/")
    marker = "/storage/"

    if marker in normalized:
        relative_path = normalized.rsplit(marker, 1)[1]
    elif normalized.startswith("storage/"):
        relative_path = normalized[len("storage/"):]
    else:
        # Do not expose arbitrary filesystem paths.
        return None

    relative = PurePosixPath(relative_path)

    if (
        relative.is_absolute()
        or not relative.parts
        or ".." in relative.parts
    ):
        return None

    return f"{PUBLIC_API_BASE_URL}/storage/{relative.as_posix()}"


def _primary_image_url(product: Product) -> str | None:
    """Return the primary active image, or the first active image."""
    images = [
        image
        for image in (product.images or [])
        if image.is_active and not image.is_deleted
    ]

    if not images:
        return None

    images.sort(
        key=lambda image: (
            not image.is_primary,
            image.sort_order,
        )
    )

    return _public_image_url(images[0].image)


class ProductService:
    def __init__(
        self,
        repo: ProductRepository,
        category_repo: CategoryRepository,
    ):
        self.repo = repo
        self.category_repo = category_repo

    # ============================================================
    # IMAGE RESPONSE HELPER
    # ============================================================

    @staticmethod
    def _with_image_url(product: Product) -> Product:
        # ProductResponse must declare image_url: str | None.
        # Pydantic can then serialize this attribute.
        product.image_url = _primary_image_url(product)
        return product

    @classmethod
    def _with_image_urls(cls, products: list[Product]) -> list[Product]:
        return [cls._with_image_url(product) for product in products]

    # ============================================================
    # CREATE PRODUCT
    # ============================================================

    async def create(
        self,
        seller_id: int,
        request: ProductCreateRequest,
    ):
        category = await self.category_repo.get_by_id(
            request.category_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        slug = slugify(request.name)

        if await self.repo.get_by_slug(slug):
            slug = f"{slug}-{uuid4().hex[:6]}"

        sku = f"KWH-{uuid4().hex[:8].upper()}"

        while await self.repo.get_by_sku(sku):
            sku = f"KWH-{uuid4().hex[:8].upper()}"

        if (
            request.discount_price is not None
            and request.discount_price >= request.price
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount price must be less than price.",
            )

        product = Product(
            seller_id=seller_id,
            category_id=request.category_id,
            name=request.name,
            slug=slug,
            sku=sku,
            description=request.description,
            price=request.price,
            discount_price=request.discount_price,
            quantity=request.quantity,
            unit=request.unit,
            brand=request.brand,
            origin=request.origin,
            is_featured=request.is_featured,
        )

        product = await self.repo.create(product)

        await self._clear_product_caches(
            product.uuid,
            seller_id,
        )

        return self._with_image_url(product)

    # ============================================================
    # GET ALL PRODUCTS
    # ============================================================

    async def get_all(self):
        products = await self.repo.get_all()
        return self._with_image_urls(products)

    # ============================================================
    # GET PRODUCT BY UUID
    # ============================================================

    async def get_by_uuid(self, uuid: str):
        product = await self.repo.get_by_uuid(uuid.strip())

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return self._with_image_url(product)

    # ============================================================
    # MY PRODUCTS
    # ============================================================

    async def my_products(self, seller_id: int):
        products = await self.repo.get_by_seller(seller_id)
        return self._with_image_urls(products)

    # ============================================================
    # UPDATE PRODUCT
    # ============================================================

    async def update(
        self,
        uuid: str,
        seller_id: int,
        request: ProductUpdateRequest,
    ):
        uuid = uuid.strip()

        product = await self.repo.get_by_uuid(uuid)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to update this product.",
            )

        data = request.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            product.name = data.pop("name")
            product.slug = slugify(product.name)

        for key, value in data.items():
            setattr(product, key, value)

        product = await self.repo.update(product)

        await self._clear_product_caches(uuid, seller_id)

        return self._with_image_url(product)

    # ============================================================
    # DELETE PRODUCT
    # ============================================================

    async def delete(
        self,
        uuid: str,
        seller_id: int,
    ):
        uuid = uuid.strip()

        product = await self.repo.get_by_uuid(uuid)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this product.",
            )

        await self.repo.delete(product)
        await self._clear_product_caches(uuid, seller_id)

        return {
            "success": True,
            "message": "Product deleted successfully.",
        }

    # ============================================================
    # CACHE INVALIDATION
    # ============================================================

    @staticmethod
    async def _clear_product_caches(
        uuid: str,
        seller_id: int,
    ) -> None:
        await cache.delete(CacheKeys.PRODUCTS)
        await cache.delete_pattern("product:*")
        await cache.delete(f"product:{uuid}")
        await cache.delete(f"seller:{seller_id}:products")
