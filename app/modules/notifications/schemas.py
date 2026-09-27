from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationType(str, Enum):
    SYSTEM = "SYSTEM"
    ORDER = "ORDER"
    PAYMENT = "PAYMENT"
    PRODUCT = "PRODUCT"
    REVIEW = "REVIEW"
    CHAT = "CHAT"


class CreateNotificationRequest(BaseModel):
    user_id: int
    title: str
    message: str
    type: NotificationType = NotificationType.SYSTEM


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    title: str
    message: str
    type: NotificationType
    is_read: bool
    created_at: datetime


class UpdateNotificationRequest(BaseModel):
    is_read: bool


class NotificationCountResponse(BaseModel):
    unread: int
    total: int


class NotificationFilter(BaseModel):
    type: Optional[NotificationType] = None
    is_read: Optional[bool] = None