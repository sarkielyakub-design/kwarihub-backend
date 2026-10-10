
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.api import api_router


# ============================================================
# REGISTER ALL SQLALCHEMY MODELS
# ============================================================

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
# PERSISTENT IMAGE STORAGE
# ============================================================

STORAGE_ROOT = Path(
    os.getenv("STORAGE_ROOT", ".")
).resolve()

STORAGE_DIR = STORAGE_ROOT / "storage"
PRODUCT_STORAGE_DIR = STORAGE_DIR / "products"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PRODUCT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CORS
# ============================================================

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://kwarihub.com",
    "https://www.kwarihub.com",
]

# Optional additional origins can be configured in Railway:
# CORS_ORIGINS=https://your-preview.vercel.app,https://example.com
extra_origins = os.getenv("CORS_ORIGINS", "")

ALLOWED_ORIGINS.extend(
    origin.strip().rstrip("/")
    for origin in extra_origins.split(",")
    if origin.strip()
)

# Remove duplicates while preserving order.
ALLOWED_ORIGINS = list(dict.fromkeys(ALLOWED_ORIGINS))


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PUBLIC STATIC FILES
# ============================================================
#
# Local:
#   STORAGE_ROOT=.
#
# Railway:
#   Attach a persistent Volume mounted at /data
#   STORAGE_ROOT=/data
#
# Example:
#   /storage/products/example.webp
#
# Public URL:
#   https://kwarihub-backend-production-ea77.up.railway.app/
#       storage/products/example.webp
#
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
# ROOT
# ============================================================

@app.get("/")
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

@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }
