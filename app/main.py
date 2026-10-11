
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.api import api_router

# Register SQLAlchemy models for Alembic discovery.
import app.database.models  # noqa: F401


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="KWARIHUB Textile Marketplace Backend API",
)


# ============================================================
# STORAGE
# ============================================================

STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", ".")).resolve()

STORAGE_DIR = STORAGE_ROOT / "storage"
PRODUCT_STORAGE_DIR = STORAGE_DIR / "products"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PRODUCT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CORS CONFIGURATION
# ============================================================
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://kwarihub.com",
    "https://www.kwarihub.com",

    # Vercel production
    "https://kwarihubfrontend.vercel.app",

    # Current Vercel preview shown in your screenshot
    "https://kwarihubfrontend-c7xtvxh0m-sarkielyakub-designs-projects.vercel.app",

    # Existing preview
    "https://kwarihubfrontend-i3vzru8lo-sarkielyakub-designs-projects.vercel.app",
]
# ============================================================
# STATIC FILE STORAGE
# ============================================================

app.mount(
    "/storage",
    StaticFiles(directory=str(STORAGE_DIR)),
    name="storage",
)


# ============================================================
# API ROUTES
# ============================================================

# Public product endpoint:
# GET /api/v1/products
#
# Public categories endpoint:
# GET /api/v1/categories
#
# Authentication endpoints are registered through api_router.

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "developer": "Ztech Universal Solution",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
    }


# ============================================================
# STORAGE DIAGNOSTIC
# ============================================================

@app.get("/health/storage", tags=["Health"])
async def storage_health():
    try:
        files = [
            item.name
            for item in PRODUCT_STORAGE_DIR.iterdir()
            if item.is_file()
        ]

        return {
            "storage_root": str(STORAGE_ROOT),
            "product_storage_dir": str(PRODUCT_STORAGE_DIR),
            "directory_exists": PRODUCT_STORAGE_DIR.is_dir(),
            "file_count": len(files),
            "sample_files": files[:10],
        }

    except OSError:
        return {
            "storage_root": str(STORAGE_ROOT),
            "product_storage_dir": str(PRODUCT_STORAGE_DIR),
            "directory_exists": False,
            "file_count": 0,
            "sample_files": [],
            "error": "Unable to read product storage directory.",
        }
