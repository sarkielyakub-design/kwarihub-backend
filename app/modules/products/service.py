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


class ProductService:
    def __init__(
        self,
        repo: ProductRepository,
        category_repo: CategoryRepository,
    ):
        self.repo = repo
        self.category_repo = category_repo

    # ================================================================
    # CREATE PRODUCT
    # ================================================================

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

        # Clear caches
        await cache.delete(CacheKeys.PRODUCTS)
        await cache.delete_pattern("product:*")
        await cache.delete(
            f"seller:{seller_id}:products",
        )

        return product

    # ================================================================
    # GET ALL PRODUCTS
    # ================================================================

    async def get_all(self):
        return await cache.remember(
            key=CacheKeys.PRODUCTS,
            callback=self.repo.get_all,
            ttl=300,
        )

    # ================================================================
    # GET PRODUCT BY UUID
    #
    # IMPORTANT:
    # Do NOT cache this SQLAlchemy object.
    #
    # The previous cache implementation was returning a serialized
    # string instead of a Product ORM object, which caused:
    #
    # ValidationError:
    # Input should be a valid dictionary or object to extract fields
    #
    # We query the repository directly here.
    # ================================================================

    async def get_by_uuid(
        self,
        uuid: str,
    ):
        uuid = uuid.strip()

        product = await self.repo.get_by_uuid(
            uuid,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return product

    # ================================================================
    # UPDATE PRODUCT
    # ================================================================

    async def update(
        self,
        uuid: str,
        seller_id: int,
        request: ProductUpdateRequest,
    ):
        uuid = uuid.strip()

        product = await self.repo.get_by_uuid(
            uuid,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not allowed to update "
                    "this product."
                ),
            )

        data = request.model_dump(
            exclude_unset=True,
        )

        if "name" in data:
            product.name = data["name"]
            product.slug = slugify(
                data["name"],
            )

        for key, value in data.items():
            if key != "name":
                setattr(
                    product,
                    key,
                    value,
                )

        product = await self.repo.update(
            product,
        )

        # Clear caches
        await cache.delete(
            CacheKeys.PRODUCTS,
        )

        await cache.delete(
            f"product:{uuid}",
        )

        await cache.delete(
            f"seller:{seller_id}:products",
        )

        return product

    # ================================================================
    # DELETE PRODUCT
    # ================================================================

    async def delete(
        self,
        uuid: str,
        seller_id: int,
    ):
        uuid = uuid.strip()

        product = await self.repo.get_by_uuid(
            uuid,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not allowed to delete "
                    "this product."
                ),
            )

        await self.repo.delete(
            product,
        )

        # Clear caches
        await cache.delete(
            CacheKeys.PRODUCTS,
        )

        await cache.delete(
            f"product:{uuid}",
        )

        await cache.delete(
            f"seller:{seller_id}:products",
        )

        return {
            "success": True,
            "message": "Product deleted successfully.",
        }

    # ================================================================
    # MY PRODUCTS
    # ================================================================

    async def my_products(
        self,
        seller_id: int,
    ):
        return await cache.remember(
            key=f"seller:{seller_id}:products",
            callback=lambda: self.repo.get_by_seller(
                seller_id,
            ),
            ttl=120,
        )