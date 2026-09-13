from pydantic import BaseModel, ConfigDict


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    product_id: int
    image: str
    is_primary: bool
    sort_order: int


class ProductImageUpdateRequest(BaseModel):
    is_primary: bool


class MessageResponse(BaseModel):
    success: bool
    message: str