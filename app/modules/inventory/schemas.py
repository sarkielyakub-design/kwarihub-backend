from pydantic import BaseModel, ConfigDict


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    product_name: str
    sku: str
    color: str
    size: str

    quantity: int

    price: float

    is_active: bool


class UpdateInventoryRequest(BaseModel):
    quantity: int


class InventoryAdjustmentRequest(BaseModel):
    quantity: int
    reason: str