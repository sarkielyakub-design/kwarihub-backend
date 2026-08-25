from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class DashboardUser(BaseModel):
    id: int
    uuid: str
    first_name: str
    last_name: str
    username: str
    email: str
    phone: str
    avatar: Optional[str] = None


class DashboardWallet(BaseModel):
    balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal


class DashboardStats(BaseModel):
    cart_count: int
    wishlist_count: int
    unread_notifications: int

    total_orders: int
    pending_orders: int
    processing_orders: int
    delivered_orders: int
    cancelled_orders: int

    total_spent: Decimal


class DashboardOrder(BaseModel):
    uuid: str
    order_number: str
    total: Decimal
    shipping_fee: Decimal
    status: str
    created_at: object


class DashboardProduct(BaseModel):
    uuid: str
    name: str
    slug: str
    price: Decimal
    discount_price: Optional[Decimal] = None
    quantity: int
    unit: str
    brand: Optional[str] = None
    is_featured: bool
    image: Optional[str] = None


class DashboardCategory(BaseModel):
    uuid: str
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_featured: bool


class DashboardResponse(BaseModel):
    user: DashboardUser
    wallet: DashboardWallet
    stats: DashboardStats

    recent_orders: list[DashboardOrder]
    featured_products: list[DashboardProduct]
    latest_products: list[DashboardProduct]
    featured_categories: list[DashboardCategory]