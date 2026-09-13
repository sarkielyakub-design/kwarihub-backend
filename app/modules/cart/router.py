from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.cart.repository import CartRepository
from app.modules.cart.schemas import (
    AddToCartRequest,
    CartItemResponse,
    CartSummaryResponse,
    MessageResponse,
    UpdateCartRequest,
)
from app.modules.cart.service import CartService
from app.modules.product_variants.repository import (
    ProductVariantRepository,
)
from app.modules.users.models import User


# ================================================================
# ROUTER
# ================================================================

router = APIRouter(
    prefix="/cart",
    tags=["Shopping Cart"],
)


# ================================================================
# SERVICE DEPENDENCY
# ================================================================

def get_service(
    db: AsyncSession = Depends(get_db),
) -> CartService:
    return CartService(
        cart_repo=CartRepository(db),
        variant_repo=ProductVariantRepository(db),
    )


# ================================================================
# ADD TO CART
# ================================================================

@router.post(
    "",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    service: CartService = Depends(
        get_service,
    ),
) -> CartItemResponse:
    """
    Add a product variant to the authenticated
    user's shopping cart.

    If the variant already exists in the cart,
    its quantity is increased.
    """

    return await service.add(
        user_id=current_user.id,
        request=request,
    )


# ================================================================
# GET CART
# ================================================================

@router.get(
    "",
    response_model=CartSummaryResponse,
)
async def get_cart(
    current_user: User = Depends(
        get_current_user,
    ),
    service: CartService = Depends(
        get_service,
    ),
) -> CartSummaryResponse:
    """
    Get the authenticated user's complete cart.

    Returns:
    - cart items
    - product information
    - variant information
    - unit prices
    - item totals
    - subtotal
    - total item quantity
    """

    return await service.get_cart(
        user_id=current_user.id,
    )


# ================================================================
# UPDATE CART ITEM
# ================================================================

@router.patch(
    "/{cart_uuid}",
    response_model=CartItemResponse,
)
async def update_cart(
    cart_uuid: str,
    request: UpdateCartRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    service: CartService = Depends(
        get_service,
    ),
) -> CartItemResponse:
    """
    Update the quantity of an existing cart item.
    """

    return await service.update(
        cart_uuid=cart_uuid,
        user_id=current_user.id,
        request=request,
    )


# ================================================================
# REMOVE CART ITEM
# ================================================================

@router.delete(
    "/{cart_uuid}",
    response_model=MessageResponse,
)
async def remove_cart_item(
    cart_uuid: str,
    current_user: User = Depends(
        get_current_user,
    ),
    service: CartService = Depends(
        get_service,
    ),
) -> MessageResponse:
    """
    Remove one item from the authenticated
    user's cart.
    """

    return await service.remove(
        cart_uuid=cart_uuid,
        user_id=current_user.id,
    )


# ================================================================
# CLEAR CART
# ================================================================

@router.delete(
    "",
    response_model=MessageResponse,
)
async def clear_cart(
    current_user: User = Depends(
        get_current_user,
    ),
    service: CartService = Depends(
        get_service,
    ),
) -> MessageResponse:
    """
    Remove all items from the authenticated
    user's cart.
    """

    return await service.clear(
        user_id=current_user.id,
    )