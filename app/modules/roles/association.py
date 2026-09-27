from sqlalchemy import Column, ForeignKey, Table

from app.database.base_model import BaseModel


role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)