
"""add promotions

Revision ID: 8d32920673ff
Revises: 226eece475fe
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d32920673ff"
down_revision: Union[str, Sequence[str], None] = "226eece475fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "promotions",
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("banner_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "promotion_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column("discount_type", sa.String(length=20), nullable=True),
        sa.Column(
            "discount_value",
            sa.Numeric(12, 2),
            nullable=True,
        ),
        sa.Column("coupon_code", sa.String(length=60), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column(
            "minimum_order_amount",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "maximum_discount_amount",
            sa.Numeric(12, 2),
            nullable=True,
        ),
        sa.Column("usage_limit", sa.Integer(), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "ends_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
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
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_index(
        "ix_promotions_uuid",
        "promotions",
        ["uuid"],
        unique=True,
    )
    op.create_index(
        "ix_promotions_coupon_code",
        "promotions",
        ["coupon_code"],
        unique=True,
    )
    op.create_index(
        "ix_promotions_product_id",
        "promotions",
        ["product_id"],
    )
    op.create_index(
        "ix_promotions_category_id",
        "promotions",
        ["category_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_promotions_category_id", table_name="promotions")
    op.drop_index("ix_promotions_product_id", table_name="promotions")
    op.drop_index("ix_promotions_coupon_code", table_name="promotions")
    op.drop_index("ix_promotions_uuid", table_name="promotions")
    op.drop_table("promotions")
