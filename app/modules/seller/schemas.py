from decimal import Decimal

from pydantic import BaseModel


class SellerDashboardResponse(BaseModel):
    total_products: int
    active_products: int

    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int

    total_sales: Decimal
    today_sales: Decimal

    total_customers: int

    average_rating: float

    out_of_stock_products: int