from pydantic import BaseModel, ConfigDict


class WishlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    user_id: int
    product_id: int


class MessageResponse(BaseModel):
    success: bool
    message: str