import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.product_images.repository import ProductImageRepository
from app.modules.product_images.schemas import (
    ProductImageResponse,
    MessageResponse,
)
from app.modules.product_images.service import ProductImageService
from app.modules.products.repository import ProductRepository
from app.modules.users.models import User

router = APIRouter(
    prefix="/products",
    tags=["Product Images"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return ProductImageService(
        image_repo=ProductImageRepository(db),
        product_repo=ProductRepository(db),
    )


UPLOAD_DIR = "storage/products"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


@router.post(
    "/{product_uuid}/images",
    response_model=ProductImageResponse,
)
async def upload_product_image(
    product_uuid: str,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ProductImageService = Depends(get_service),
):
    extension = image.filename.split(".")[-1].lower()

    if extension not in [
        "jpg",
        "jpeg",
        "png",
        "webp",
    ]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format.",
        )

    filename = (
        f"{uuid.uuid4()}.{extension}"
    )

    path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    with open(path, "wb") as buffer:
        buffer.write(await image.read())

    return await service.upload(
        product_uuid=product_uuid,
        seller_id=current_user.id,
        image_path=path,
    )


@router.get(
    "/{product_uuid}/images",
    response_model=list[ProductImageResponse],
)
async def get_product_images(
    product_uuid: str,
    service: ProductImageService = Depends(get_service),
):
    return await service.get_product_images(
        product_uuid,
    )


@router.patch(
    "/images/{image_uuid}/primary",
    response_model=ProductImageResponse,
)
async def make_primary(
    image_uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProductImageService = Depends(get_service),
):
    return await service.make_primary(
        image_uuid,
        current_user.id,
    )


@router.delete(
    "/images/{image_uuid}",
    response_model=MessageResponse,
)
async def delete_image(
    image_uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProductImageService = Depends(get_service),
):
    return await service.delete(
        image_uuid,
        current_user.id,
    )