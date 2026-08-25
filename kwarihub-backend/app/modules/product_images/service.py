from fastapi import HTTPException, UploadFile

from app.modules.products.repository import ProductRepository
from app.modules.product_images.models import ProductImage
from app.modules.product_images.repository import ProductImageRepository


class ProductImageService:
    def __init__(
        self,
        image_repo: ProductImageRepository,
        product_repo: ProductRepository,
    ):
        self.image_repo = image_repo
        self.product_repo = product_repo

    async def upload(
        self,
        product_uuid: str,
        seller_id: int,
        image_path: str,
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
                detail="You are not allowed to upload images for this product.",
            )

        images = await self.image_repo.get_product_images(product.id)

        product_image = ProductImage(
            product_id=product.id,
            image=image_path,
            is_primary=len(images) == 0,
            sort_order=len(images) + 1,
        )

        return await self.image_repo.create(product_image)

    async def get_product_images(
        self,
        product_uuid: str,
    ):
        product = await self.product_repo.get_by_uuid(product_uuid)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found.",
            )

        return await self.image_repo.get_product_images(product.id)

    async def make_primary(
        self,
        image_uuid: str,
        seller_id: int,
    ):
        image = await self.image_repo.get_by_uuid(image_uuid)

        if not image:
            raise HTTPException(
                status_code=404,
                detail="Image not found.",
            )

        product = await self.product_repo.get_by_uuid(image.product.uuid)

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        await self.image_repo.remove_primary(product.id)

        image.is_primary = True

        return await self.image_repo.update(image)

    async def delete(
        self,
        image_uuid: str,
        seller_id: int,
    ):
        image = await self.image_repo.get_by_uuid(image_uuid)

        if not image:
            raise HTTPException(
                status_code=404,
                detail="Image not found.",
            )

        product = await self.product_repo.get_by_uuid(image.product.uuid)

        if product.seller_id != seller_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized.",
            )

        await self.image_repo.delete(image)

        return {
            "success": True,
            "message": "Image deleted successfully.",
        }