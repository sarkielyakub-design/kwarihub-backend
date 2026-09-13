from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.seller.repository import SellerRepository
from app.modules.seller.schemas import SellerDashboardResponse
from app.modules.seller.service import SellerService
from app.modules.users.models import User

router = APIRouter(
    prefix="/seller",
    tags=["Seller Dashboard"],
)


def get_service(
    db: AsyncSession = Depends(get_db),
):
    return SellerService(
        SellerRepository(db),
    )


@router.get(
    "/dashboard",
    response_model=SellerDashboardResponse,
)
async def dashboard(
    current_user: User = Depends(get_current_user),
    service: SellerService = Depends(get_service),
):
    return await service.dashboard(
        current_user.id,
    )