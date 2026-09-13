from pathlib import Path

BASE = Path(".")

folders = [
    "app",

    "app/api",
    "app/api/v1",

    "app/api/v1/auth",
    "app/api/v1/admin",
    "app/api/v1/customer",
    "app/api/v1/vendor",
    "app/api/v1/shop",
    "app/api/v1/category",
    "app/api/v1/product",
    "app/api/v1/cart",
    "app/api/v1/wishlist",
    "app/api/v1/order",
    "app/api/v1/payment",
    "app/api/v1/wallet",
    "app/api/v1/review",
    "app/api/v1/search",
    "app/api/v1/dashboard",
    "app/api/v1/notification",
    "app/api/v1/support",

    "app/core",
    "app/database",
    "app/models",
    "app/schemas",
    "app/services",
    "app/repositories",
    "app/security",
    "app/utils",
    "app/dependencies",
    "app/middleware",
    "app/events",
    "app/websocket",
    "app/workers",

    "alembic",
    "tests",
    "uploads",
    "docs",
    "scripts",
    "docker"
]

files = [

    ".env",
    ".env.example",
    "requirements.txt",
    "README.md",
    "alembic.ini",

    "app/main.py",

    "app/core/config.py",
    "app/core/security.py",

    "app/database/base.py",
    "app/database/session.py",

    "app/models/__init__.py",
    "app/schemas/__init__.py",
    "app/services/__init__.py",
    "app/repositories/__init__.py",

    "app/api/__init__.py",
    "app/api/v1/__init__.py",

    "app/api/v1/auth/router.py",
    "app/api/v1/admin/router.py",
    "app/api/v1/customer/router.py",
    "app/api/v1/vendor/router.py",
    "app/api/v1/shop/router.py",
    "app/api/v1/category/router.py",
    "app/api/v1/product/router.py",
    "app/api/v1/cart/router.py",
    "app/api/v1/wishlist/router.py",
    "app/api/v1/order/router.py",
    "app/api/v1/payment/router.py",
    "app/api/v1/wallet/router.py",
    "app/api/v1/review/router.py",
    "app/api/v1/search/router.py",
    "app/api/v1/dashboard/router.py",
    "app/api/v1/notification/router.py",
    "app/api/v1/support/router.py",
]

for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

for file in files:
    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print("🎉 KWARIHUB Backend Structure Created Successfully!")