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
#
# This imports all concrete models and registers them with:
#
#     app.database.base.Base.metadata
#
# Required for SQLAlchemy / Alembic model discovery.
#
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
# STORAGE CONFIGURATION
# ============================================================
#
# LOCAL:
#
#     STORAGE_ROOT=.
#
# Files:
#
#     ./storage/products/
#
#
# RAILWAY:
#
# Create a Railway Volume mounted at:
#
#     /data
#
# Then set:
#
#     STORAGE_ROOT=/data
#
# Files:
#
#     /data/storage/products/
#
# ============================================================

STORAGE_ROOT = Path(
    os.getenv(
        "STORAGE_ROOT",
        ".",
    )
).resolve()


STORAGE_DIR = STORAGE_ROOT / "storage"


PRODUCT_STORAGE_DIR = STORAGE_DIR / "products"


# ============================================================
# CREATE STORAGE DIRECTORIES
# ============================================================

STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PRODUCT_STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC FILES
# ============================================================
#
# URL:
#
#     /storage/...
#
# maps to:
#
#     STORAGE_ROOT/storage/...
#
# Example:
#
#     /storage/products/example.jpg
#
# maps to:
#
#     /data/storage/products/example.jpg
#
# on Railway when STORAGE_ROOT=/data.
#
# FastAPI's StaticFiles serves files from the configured
# directory under the mounted URL path.
#
# ============================================================

app.mount(
    "/storage",
    StaticFiles(
        directory=str(STORAGE_DIR),
    ),
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