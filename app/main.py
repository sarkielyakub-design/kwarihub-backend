
from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.api import api_router

# Register SQLAlchemy models for Alembic discovery.
import app.database.models  # noqa: F401


logger = logging.getLogger(__name__)


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
    "https://kwarihubfrontend.vercel.app",
    "https://kwarihubfrontend-c7xtvxh0m-sarkielyakub-designs-projects.vercel.app",
    "https://kwarihubfrontend-i3vzru8lo-sarkielyakub-designs-projects.vercel.app",
]

extra_origins = os.getenv("CORS_ORIGINS", "")

EXTRA_ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in extra_origins.split(",")
    if origin.strip()
]

ALLOWED_ORIGINS = list(
    dict.fromkeys(
        origin.rstrip("/")
        for origin in DEFAULT_ALLOWED_ORIGINS + EXTRA_ALLOWED_ORIGINS
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        logger.exception("Unable to inspect product storage")

        return {
            "storage_root": str(STORAGE_ROOT),
            "product_storage_dir": str(PRODUCT_STORAGE_DIR),
            "directory_exists": False,
            "file_count": 0,
            "sample_files": [],
            "error": "Unable to read product storage directory.",
        }


# ============================================================
# PROMOTIONS ROUTE DIAGNOSTIC
# ============================================================

@app.on_event("startup")
async def log_registered_promotion_routes():
    promotion_routes = [
        {
            "path": route.path,
            "methods": sorted(route.methods or []),
        }
        for route in app.routes
        if hasattr(route, "path")
        and "promotion" in route.path.lower()
    ]

    if promotion_routes:
        logger.info(
            "Registered promotion routes: %s",
            promotion_routes,
        )
    else:
        logger.error(
            "No promotion routes registered. "
            "Check app.api.v1.api and the promotions router imports."
        )
