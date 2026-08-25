from decimal import Decimal

from pydantic import BaseModel


# ==========================
# Admin Dashboard
# ==========================

class DashboardResponse(BaseModel):
    total_users: int
    total_sellers: int
    total_products: int
    total_categories: int
    total_orders: int
    total_payments: int
    total_withdrawals: int
    total_reviews: int

    total_revenue: Decimal

    pending_withdrawals: int
    pending_products: int


# ==========================
# Revenue Report
# ==========================

class RevenueReportResponse(BaseModel):
    today: Decimal
    this_week: Decimal
    this_month: Decimal
    this_year: Decimal


# ==========================
# Marketplace Analytics
# ==========================

class MarketplaceAnalyticsResponse(BaseModel):
    total_users: int
    total_sellers: int
    total_products: int
    total_orders: int
    total_completed_orders: int
    total_pending_orders: int

    total_revenue: Decimal