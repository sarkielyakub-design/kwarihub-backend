"""KWARIHUB - wishlist - router.py"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.products.repository import ProductRepository
from app.modules.users.models import User
from app.modules.wishlist.repository import WishlistRepository
from app.modules.wishlist.schemas import (
    WishlistResponse,
    MessageResponse,
)
from app.modules.wishlist.service import WishlistService

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return WishlistService(
        wishlist_repo=WishlistRepository(db),
        product_repo=ProductRepository(db),
    )


@router.post(
    "/{product_uuid}",
    response_model=WishlistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_wishlist(
    product_uuid: str,
    current_user: User = Depends(get_current_user),
    service: WishlistService = Depends(get_service),
):
    return await service.add(
        product_uuid=product_uuid,
        user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[WishlistResponse],
)
async def get_my_wishlist(
    current_user: User = Depends(get_current_user),
    service: WishlistService = Depends(get_service),
):
    return await service.get_all(
        current_user.id,
    )


@router.delete(
    "/{product_uuid}",
    response_model=MessageResponse,
)
async def remove_from_wishlist(
    product_uuid: str,
    current_user: User = Depends(get_current_user),
    service: WishlistService = Depends(get_service),
):
    return await service.remove(
        product_uuid=product_uuid,
        user_id=current_user.id,
    )