"""add monnify payment fields

Revision ID: 8cce3f9802ca
Revises: a5da3b641cdf
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8cce3f9802ca"
down_revision: Union[str, Sequence[str], None] = "a5da3b641cdf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column(
            "transaction_reference",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "payments",
        sa.Column(
            "checkout_url",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "payments",
        sa.Column(
            "payment_method",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_payments_transaction_reference",
        "payments",
        ["transaction_reference"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_payments_transaction_reference",
        table_name="payments",
    )

    op.drop_column(
        "payments",
        "payment_method",
    )

    op.drop_column(
        "payments",
        "checkout_url",
    )

    op.drop_column(
        "payments",
        "transaction_reference",
    )