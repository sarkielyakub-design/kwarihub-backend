from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_featured: bool = False


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    parent_id: Optional[int]
    sort_order: int
    is_featured: bool
    is_active: bool


class CategoryListResponse(BaseModel):
    success: bool
    data: list[CategoryResponse]


class MessageResponse(BaseModel):
    success: bool
    message: str