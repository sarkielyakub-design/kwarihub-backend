from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

from app.modules.auth.dependencies import get_current_user

from app.modules.product_images.repository import ProductImageRepository
from app.modules.product_images.schemas import (
    MessageResponse,
    ProductImageResponse,
)
from app.modules.product_images.service import ProductImageService

from app.modules.products.repository import ProductRepository

from app.modules.users.models import User


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/products",
    tags=["Product Images"],
)


# ============================================================
# SERVICE
# ============================================================

def get_service(
    db: AsyncSession = Depends(get_db),
) -> ProductImageService:
    return ProductImageService(
        image_repo=ProductImageRepository(db),
        product_repo=ProductRepository(db),
    )


# ============================================================
# STORAGE CONFIGURATION
# ============================================================
#
# Railway:
#
#   STORAGE_ROOT=/data
#
# With a Railway Volume mounted at:
#
#   /data
#
# images will be stored permanently at:
#
#   /data/storage/products
#
# Local development:
#
#   STORAGE_ROOT=.
#
# results in:
#
#   ./storage/products
#
# ============================================================

STORAGE_ROOT = os.getenv(
    "STORAGE_ROOT",
    ".",
)

UPLOAD_DIR = Path(
    STORAGE_ROOT,
) / "storage" / "products"


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMAGE CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


# ============================================================
# UPLOAD PRODUCT IMAGE
# ============================================================

@router.post(
    "/{product_uuid}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_image(
    product_uuid: str,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ProductImageService = Depends(get_service),
):
    # --------------------------------------------------------
    # Validate content type
    # --------------------------------------------------------

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported image type. "
                "Only JPG, JPEG, PNG and WEBP are allowed."
            ),
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    original_filename = image.filename or ""

    extension = (
        Path(original_filename)
        .suffix
        .lower()
        .lstrip(".")
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported image format. "
                "Only JPG, JPEG, PNG and WEBP are allowed."
            ),
        )

    # --------------------------------------------------------
    # Generate safe filename
    # --------------------------------------------------------

    filename = f"{uuid.uuid4()}.{extension}"

    file_path = UPLOAD_DIR / filename

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    contents = await image.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )

    # --------------------------------------------------------
    # Validate size
    # --------------------------------------------------------

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size cannot exceed 10 MB.",
        )

    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    try:
        with file_path.open("wb") as buffer:
            buffer.write(contents)

    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save image.",
        ) from exc

    # --------------------------------------------------------
    # Store image reference in database
    #
    # IMPORTANT:
    # We pass the storage path expected by the existing service.
    # --------------------------------------------------------

    return await service.upload(
        product_uuid=product_uuid,
        seller_id=current_user.id,
        image_path=str(file_path),
    )


# ============================================================
# GET PRODUCT IMAGES
# ============================================================

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


# ============================================================
# MAKE IMAGE PRIMARY
# ============================================================

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


# ============================================================
# DELETE IMAGE
# ============================================================

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