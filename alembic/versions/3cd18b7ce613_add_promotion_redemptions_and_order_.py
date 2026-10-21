
"""Add promotion redemptions and order discounts.

Revision ID: 3cd18b7ce613
Revises: 8d32920673ff
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3cd18b7ce613"
down_revision: Union[str, Sequence[str], None] = "8d32920673ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add discount fields to existing orders.
    op.add_column(
        "orders",
        sa.Column(
            "discount_amount",
            sa.Numeric(12, 2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
    )
    op.add_column(
        "orders",
        sa.Column("coupon_code", sa.String(60), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("promotion_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        "ix_orders_coupon_code",
        "orders",
        ["coupon_code"],
        unique=False,
    )
    op.create_index(
        "ix_orders_promotion_id",
        "orders",
        ["promotion_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_orders_promotion_id_promotions",
        "orders",
        "promotions",
        ["promotion_id"],
        ["id"],
    )

    # Record coupon/promotion usage against an order.
    op.create_table(
        "promotion_redemptions",
        sa.Column("promotion_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column("coupon_code", sa.String(60), nullable=True),
        sa.Column(
            "discount_amount",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "redeemed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.false(),
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
            ["promotion_id"],
            ["promotions.id"],
            name="fk_promotion_redemptions_promotion_id",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name="fk_promotion_redemptions_order_id",
        ),
        sa.ForeignKeyConstraint(
            ["buyer_id"],
            ["users.id"],
            name="fk_promotion_redemptions_buyer_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", name="uq_promotion_redemptions_order_id"),
        sa.UniqueConstraint("uuid", name="uq_promotion_redemptions_uuid"),
    )

    op.create_index(
        "ix_promotion_redemptions_promotion_id",
        "promotion_redemptions",
        ["promotion_id"],
        unique=False,
    )
    op.create_index(
        "ix_promotion_redemptions_buyer_id",
        "promotion_redemptions",
        ["buyer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_promotion_redemptions_buyer_id",
        table_name="promotion_redemptions",
    )
    op.drop_index(
        "ix_promotion_redemptions_promotion_id",
        table_name="promotion_redemptions",
    )
    op.drop_table("promotion_redemptions")

    op.drop_constraint(
        "fk_orders_promotion_id_promotions",
        "orders",
        type_="foreignkey",
    )
    op.drop_index("ix_orders_promotion_id", table_name="orders")
    op.drop_index("ix_orders_coupon_code", table_name="orders")

    op.drop_column("orders", "promotion_id")
    op.drop_column("orders", "coupon_code")
    op.drop_column("orders", "discount_amount")
