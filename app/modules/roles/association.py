from sqlalchemy import (
    Column,
    ForeignKey,
    Table,
)

from app.database.base_model import BaseModel


# ============================================================
# ROLE -> PERMISSION
# ============================================================

role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,

    Column(
        "role_id",
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),

    Column(
        "permission_id",
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


# ============================================================
# USER -> ROLE
# ============================================================

user_roles = Table(
    "user_roles",
    BaseModel.metadata,

    Column(
        "user_id",
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),

    Column(
        "role_id",
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)