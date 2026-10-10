
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
from fastapi.responses import FileResponse
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


router = APIRouter(prefix="/products", tags=["Product Images"])

STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", ".")).resolve()
UPLOAD_DIR = STORAGE_ROOT / "storage" / "products"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def get_service(
    db: AsyncSession = Depends(get_db),
) -> ProductImageService:
    return ProductImageService(
        image_repo=ProductImageRepository(db),
        product_repo=ProductRepository(db),
    )


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
    content_type = (image.content_type or "").lower()
    extension = Path(image.filename or "").suffix.lower().lstrip(".")

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are allowed.",
        )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image extension.",
        )

    contents = await image.read(MAX_IMAGE_SIZE + 1)
    await image.close()

    if not contents:
        raise HTTPException(status_code=400, detail="Image is empty.")

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size cannot exceed 10 MB.",
        )

    # Check the file signature rather than trusting only its extension.
    signatures = {
        "image/jpeg": contents.startswith(b"\xff\xd8\xff"),
        "image/png": contents.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": (
            len(contents) >= 12
            and contents[:4] == b"RIFF"
            and contents[8:12] == b"WEBP"
        ),
    }
    if not signatures.get(content_type, False):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not match its image type.",
        )

    # Use the canonical extension for the validated content type.
    filename = f"{uuid.uuid4()}{ALLOWED_CONTENT_TYPES[content_type]}"
    file_path = UPLOAD_DIR / filename

    try:
        file_path.write_bytes(contents)
        result = await service.upload(
            product_uuid=product_uuid,
            seller_id=current_user.id,
            image_path=f"/storage/products/{filename}",
        )
        return result
    except Exception:
        # Avoid leaving an orphaned file when the database operation fails.
        file_path.unlink(missing_ok=True)
        raise


@router.get("/images/files/{filename}")
async def serve_product_image(filename: str):
    # Prevent directory traversal and arbitrary file reads.
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    path = (UPLOAD_DIR / filename).resolve()

    if path.parent != UPLOAD_DIR.resolve() or not path.is_file():
        raise HTTPException(status_code=404, detail="Image not found.")

    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    media_type = media_types.get(path.suffix.lower())

    if not media_type:
        raise HTTPException(status_code=404, detail="Image not found.")

    return FileResponse(
        path,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get(
    "/{product_uuid}/images",
    response_model=list[ProductImageResponse],
)
async def get_product_images(
    product_uuid: str,
    service: ProductImageService = Depends(get_service),
):
    return await service.get_product_images(product_uuid)


@router.patch(
    "/images/{image_uuid}/primary",
    response_model=ProductImageResponse,
)
async def make_primary(
    image_uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProductImageService = Depends(get_service),
):
    return await service.make_primary(image_uuid, current_user.id)


@router.delete(
    "/images/{image_uuid}",
    response_model=MessageResponse,
)
async def delete_image(
    image_uuid: str,
    current_user: User = Depends(get_current_user),
    service: ProductImageService = Depends(get_service),
):
    return await service.delete(image_uuid, current_user.id)
