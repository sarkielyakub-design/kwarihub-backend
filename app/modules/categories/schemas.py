from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE
# ============================================================

class CategoryCreateRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    description: Optional[str] = None

    icon: Optional[str] = None

    parent_id: Optional[int] = None

    sort_order: int = 0

    is_featured: bool = False


# ============================================================
# UPDATE
# ============================================================

class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=150,
    )

    description: Optional[str] = None

    icon: Optional[str] = None

    parent_id: Optional[int] = None

    sort_order: Optional[int] = None

    is_featured: Optional[bool] = None

    is_active: Optional[bool] = None


# ============================================================
# RESPONSE
# ============================================================

class CategoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    uuid: str

    name: str

    slug: str

    description: Optional[str] = None

    icon: Optional[str] = None

    parent_id: Optional[int] = None

    sort_order: int

    is_featured: bool

    is_active: bool


# ============================================================
# LIST RESPONSE
# ============================================================

class CategoryListResponse(BaseModel):
    success: bool

    data: list[CategoryResponse]


# ============================================================
# MESSAGE
# ============================================================

class MessageResponse(BaseModel):
    success: bool

    message: str