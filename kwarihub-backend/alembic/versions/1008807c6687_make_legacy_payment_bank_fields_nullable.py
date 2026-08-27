"""make legacy payment bank fields nullable

Revision ID: REPLACE_WITH_GENERATED_REVISION
Revises: 8cce3f9802ca
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f1234567890"
down_revision: Union[str, Sequence[str], None] = "8cce3f9802ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Make legacy bank fields nullable.

    Monnify checkout payments do not require these fields.
    They are no longer part of the Payment SQLAlchemy model,
    but they still exist in the existing database table.
    """

    op.alter_column(
        "payments",
        "bank_code",
        existing_type=sa.String(length=50),
        nullable=True,
    )

    op.alter_column(
        "payments",
        "bank_name",
        existing_type=sa.String(length=100),
        nullable=True,
    )

    op.alter_column(
        "payments",
        "account_name",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    op.alter_column(
        "payments",
        "account_number",
        existing_type=sa.String(length=30),
        nullable=True,
    )


def downgrade() -> None:
    """
    Restore the legacy fields to NOT NULL.

    This assumes there are no NULL values when downgrading.
    """

    op.alter_column(
        "payments",
        "bank_code",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.alter_column(
        "payments",
        "bank_name",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "payments",
        "account_name",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "payments",
        "account_number",
        existing_type=sa.String(length=30),
        nullable=False,
    )