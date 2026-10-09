"""add rbac tables and vendors

Revision ID: 226eece475fe
Revises: efa350962d61
Create Date: 2026-10-07 13:08:58.354305

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "226eece475fe"
down_revision: Union[str, Sequence[str], None] = "efa350962d61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------
    op.create_table(
        "permissions",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(
        op.f("ix_permissions_uuid"),
        "permissions",
        ["uuid"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # Role <-> Permission
    # ------------------------------------------------------------------
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # ------------------------------------------------------------------
    # User <-> Role
    # ------------------------------------------------------------------
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    # ------------------------------------------------------------------
    # Vendors
    # ------------------------------------------------------------------
    op.create_table(
        "vendors",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("business_name", sa.String(length=255), nullable=False),
        sa.Column(
            "business_description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "business_phone",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "business_email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "country",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "city",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "address",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPROVED",
                "REJECTED",
                "SUSPENDED",
                name="vendorstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "rejection_reason",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "admin_note",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "reviewed_by",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "rejected_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "suspended_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_vendors_status"),
        "vendors",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_vendors_user_id"),
        "vendors",
        ["user_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_vendors_uuid"),
        "vendors",
        ["uuid"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Vendors
    op.drop_index(
        op.f("ix_vendors_uuid"),
        table_name="vendors",
    )

    op.drop_index(
        op.f("ix_vendors_user_id"),
        table_name="vendors",
    )

    op.drop_index(
        op.f("ix_vendors_status"),
        table_name="vendors",
    )

    op.drop_table("vendors")

    # User <-> Role
    op.drop_table("user_roles")

    # Role <-> Permission
    op.drop_table("role_permissions")

    # Permissions
    op.drop_index(
        op.f("ix_permissions_uuid"),
        table_name="permissions",
    )

    op.drop_table("permissions")

    # PostgreSQL enum created for VendorStatus
    sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SUSPENDED",
        name="vendorstatus",
    ).drop(op.get_bind(), checkfirst=True)
    